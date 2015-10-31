""" FuzzyFilePath - autocomplete filepaths



    # tasks

        - growing list of triggers is getting unmaintainable. Probably group by main-scope in object for faster
            retrieval and namespacing
        - add custom triggers without overriding the default scopes
        - support of multiple project folders may be achieved by hooking into settings-folders-array

        - improve testing
        - add to command palette: settings, base_directory
        - test: reload settings on change


    @version 0.2.4
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re
import os

from FuzzyFilePath.project.ProjectManager import ProjectManager
from FuzzyFilePath.project.Project import Project
from FuzzyFilePath.project.CurrentFile import CurrentFile
import FuzzyFilePath.expression as Context
import FuzzyFilePath.project.validate as Validate
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.verbose import log
from FuzzyFilePath.common.config import config
import FuzzyFilePath.common.selection as Selection
import FuzzyFilePath.common.path as Path
import FuzzyFilePath.common.settings as Settings
from FuzzyFilePath.common.string import get_diff

scope_cache = {}

ID = "FuzzyFilePath"


def plugin_loaded():
    """ load settings """
    update_settings()
    global_settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
    global_settings.add_on_change("update", update_settings)


def update_settings():
    """ restart projectFiles with new plugin and project settings """

    # invalidate cache
    global scope_cache
    scope_cache = {}
    # update settings
    global_settings = Settings.update()
    # update project settings
    ProjectManager.initialize(Project, global_settings)


class Completion:
    """
        Manage active state of completion and post cleanup
    """
    active = False  # completion currently in progress (servce suggestions)
    onInsert = []   # substitutions for building final path
    base_directory = False  # base directory to set for absolute path, enabled by query...

    def start(post_replacements=[]):
        Completion.replaceOnInsert = post_replacements
        Completion.active = True

    def stop():
        Completion.active = False
        # set by query....
        Completion.base_directory = False

    def is_active():
        return Completion.active

    def get_final_path(path):
        # hack reverse
        path = re.sub(config["ESCAPE_DOLLAR"], "$", path)
        for replace in Completion.replaceOnInsert:
            path = re.sub(replace[0], replace[1], path)

        if Completion.base_directory and path.startswith("/"):
            path = re.sub("^\/" + Completion.base_directory, "", path)
            path = Path.sanitize(path)

        return path


class InsertPathCommand(sublime_plugin.TextCommand):
    """ trigger customized autocomplete overriding auto settings """
    def run(self, edit, type="default", base_directory=None, replace_on_insert=[], extensions=[]):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        Query.force("filepath_type", type)
        Query.force("base_directory", base_directory)

        if len(replace_on_insert) > 0:
            Query.force("replace_on_insert", replace_on_insert)
        if len(extensions) > 0:
            Query.force("extensions", extensions)

        self.view.run_command('auto_complete', "insert")


class Query:
    """
        Build current query based on received modifiers
    """
    forces = {
        # documentation only, will be removed
        "filepath_type": False,
        "extensions": [],
        "base_directory": "",
        "replace_on_insert": []
    }

    extensions = ["*"]
    base_path = False
    replace_on_insert = []

    def reset():
        Query.extensions = ["*"]
        Query.base_path = False
        Query.replace_on_insert = []
        Query.forces.clear()

    def force(key, value):
        Query.forces[key] = value

    def get(key, default=None):
        return Query.forces.get(key, default)

    def by_command():
        return bool(Query.get("filepath_type", False))

    def build(needle, trigger, current_folder, project_folder):

        query = {}

        force_type = Query.get("filepath_type", False)
        triggered = Query.by_command()
        filepath_type = "relative"
        needle = Path.sanitize(needle)
        needle_is_absolute = Path.is_absolute(needle)
        needle_is_relative = Path.is_relative(needle)
        needle_is_path = needle_is_absolute or needle_is_relative
        # abort if autocomplete is not available
        if not triggered and trigger.get("auto", False) is False and needle_is_path is False:
            # verbose("FFP no autocomplete")
            return False
        # test path to trigger auto-completion by needle
        if not triggered and trigger["auto"] is False and config["AUTO_TRIGGER"] and needle_is_absolute:
            force_type = "absolute"
        # base_directory: override - trigger - False
        base_directory = trigger.get("base_directory", False)
        base_directory = Query.get("base_directory", base_directory)
        #
        # set current directory by force, else by trigger:
        #
        # trigger       |
        # --------------|--------------------
        # False         | use current file's directory
        # True          | use settings: base_directory
        # String        | use string as base_directory
        # change base folder to base directory
        #
        if base_directory is True:
            current_folder = config["BASE_DIRECTORY"]
        elif base_directory:
            current_folder = Path.sanitize_base_directory(base_directory)
        # notify completion to replace path
        if base_directory and needle_is_absolute:
            Completion.base_directory = current_folder
        #
        # filepath_type
        #
        # needle    | trigger rel   | force     | RESULT
        # ----------|---------------|-----------|---------
        # ?         | relative      | False     | relative
        # ?         | absolute      | False     | absolute
        # absolute  | *             | False     | absolute
        # relative  | *             | False     | relative
        # *         | *             | relative  | relative
        # *         | *             | absolute  | absolute
        #
        if force_type:
            filepath_type = force_type
        elif needle_is_absolute:
            filepath_type = "absolute"
        elif needle_is_relative:
            filepath_type = "relative"
        elif trigger.get("relative") is True:
            filepath_type = "relative"
        elif trigger.get("relative") is False:
            filepath_type = "absolute"

        Query.base_path = current_folder if filepath_type == "relative" else False

        # replacements: override - trigger - None
        Query.replace_on_insert = trigger.get("replace_on_insert", [])
        Query.replace_on_insert = Query.get("replace_on_insert", Query.replace_on_insert)
        # extensions: override - trigger - "js"
        extensions = trigger.get("extensions", ["*"])
        extensions = Query.get("extensions", extensions)
        Query.extensions = extensions
        Query.needle = Query.build_needle_query(needle, current_folder)
        # strip any starting dots or slashes
        Query.needle = re.sub("^[\.\/]*", "", Query.needle)
        # --------------------------------------------------------------------
        # tests throw error if results are set to class
        # Require refactoring of static classes with dynamic properties?
        # --------------------------------------------------------------------
        query["extensions"] = extensions
        query["base_path"] = current_folder if filepath_type == "relative" else False
        query["needle"] = Query.build_needle_query(needle, current_folder)

        if triggered or (config["AUTO_TRIGGER"] if needle_is_path else trigger.get("auto", config["AUTO_TRIGGER"])):
            return query

        return False

    def build_needle_query(needle, current_folder):
        """
            sanitizes requested path and replaces a starting ./ with the current (local) folder
            returns final needle
        """
        current_folder = "" if not current_folder else current_folder
        needle = re.sub("\.\./", "", needle)
        needle = re.sub("[\\n\\t]", "", needle)

        # remove base path from needle
        if isinstance(current_folder, str) and needle.startswith(current_folder):
            needle = needle[len(Query.base_path):]

        needle = needle.strip()

        if needle.startswith("./"):
            needle = current_folder + re.sub("\.\/", "", needle)

        return needle


def get_matching_autotriggers(scope, triggers):
    global scope_cache
    # get cached evaluation
    result = scope_cache.get(scope)
    if result is None:
        # evaluate triggers on current scope
        result = [trigger for trigger in triggers if trigger.get("auto") and re.search(trigger.get("scope"), scope)]
        # add to cache
        scope_cache[scope] = result if len(result) > 0 else False
        result = scope_cache.get(scope)

    return result


class FuzzyFilePath():

    def completion_active():
        return Completion.is_active()

    def completion_stop():
        Completion.stop()

    def on_query_completions(view, project_folder, current_folder):
        global Context, Selection

        current_scope = Selection.get_scope(view)

        if not Query.by_command():
            triggers = get_matching_autotriggers(current_scope, config["TRIGGER"])
        else:
            triggers = config["TRIGGER"]

        if not bool(triggers):
            verbose(ID, "abort query, no valid scope-regex for current context")
            return False

        # parse current context, may contain 'is_valid: False'
        expression = Context.get_context(view)
        if expression["error"] and not Query.by_command():
            verbose(ID, "abort not a valid context")
            return False

        # check if there is a trigger for the current expression
        trigger = Context.find_trigger(expression, current_scope, triggers)
        # verbose("trigger", trigger)

        # expression | trigger  | force | ACTION            | CURRENT
        # -----------|----------|-------|-------------------|--------
        # invalid    | False    | False | abort             | abort
        # invalid    | False    | True  | query needle      | abort
        # invalid    | True     | False | query             |
        # invalid    | True     | True  | query +override   |
        # valid      | False    | False | abort             | abort
        # valid      | False    | True  | query needle      | abort
        # valid      | True     | False | query             |
        # valid      | True     | True  | query +override   |

        # currently trigger is required in Query.build
        if trigger is False:
            verbose(ID, "abort completion, no trigger found")
            return False

        if not expression["valid_needle"]:
            word = Selection.get_word(view)
            expression["needle"] = re.sub("[^\.A-Za-z0-9\-\_$]", "", word)
            verbose(ID, "changed invalid needle to {0}".format(expression["needle"]))
        else:
            verbose(ID, "context evaluation {0}".format(expression))

        if Query.build(expression.get("needle"), trigger, current_folder, project_folder) is False:
            # query is valid, but may not be triggered: not forced, no auto-options
            verbose(ID, "abort valid query: auto trigger disabled")
            return False

        verbose(ID, ".───────────────────────────────────────────────────────────────")
        verbose(ID, "| scope settings: {0}".format(trigger))
        verbose(ID, "| search needle: '{0}'".format(Query.needle))
        verbose(ID, "| in base path: '{0}'".format(Query.base_path))

        FuzzyFilePath.start_expression = expression
        completions = ProjectManager.search_completions(Query.needle, project_folder, Query.extensions, Query.base_path)

        if completions and len(completions[0]) > 0:
            Completion.start(Query.replace_on_insert)
            view.run_command('_enter_insert_mode') # vintageous
            log("| => {0} completions found".format(len(completions)))
        else:
            sublime.status_message("FFP no filepaths found for '" + Query.needle + "'")
            Completion.stop()
            log("| => no valid files found for needle: {0}".format(Query.needle))

        log("")

        Query.reset()
        return completions

    def on_post_insert_completion(view, post_remove):
        start_expression = FuzzyFilePath.start_expression
        expression = Context.get_context(view)

        # diff of previous needle and inserted needle
        diff = get_diff(post_remove, expression["needle"])
        # cleanup string
        final_path = re.sub("^" + diff["start"], "", expression["needle"])
        # do not replace current word
        if diff["end"] != start_expression["word"]:
            final_path = re.sub(diff["end"] + "$", "", final_path)

        # remove path query completely
        final_path = Completion.get_final_path(final_path)
        log("post cleanup path:'", expression.get("needle"), "' ~~> '", final_path, "'")

        # replace current query with final path
        view.run_command("ffp_replace_region", {
            "a": expression["region"].a,
            "b": expression["region"].b,
            "string": final_path,
            "move_cursor": True
        })
