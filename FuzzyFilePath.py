""" FuzzyFilePath - autocomplete filepaths

    # refactor query

        > keep track of changes and insights through testing (probably needs improvement)

        - make code readable again by improving naming and removing temp variables, duplicates
        - reduce dependencies via properties and decrease messages
        - circular dependencies for completion in ffp and query as module (requires completion)
        - config misbehaviour (scopes: .js) if config is references in module query and module completion
        => 1a. refactor config session object or
        => 1b. resolve circular dependencies ffo controller object (@see refactor event flow)
        => 2. create modules query and completion (temp) until further understanding of those modules (...simplfy)

    # tasks

        - growing list of triggers is getting unmaintainable. Probably group by main-scope in object for faster
            retrieval and namespacing
        - add custom triggers without overriding the default scopes
        - support of multiple project folders may be achieved by hooking into settings-folders-array

        - improve testing
        - add to command palette: settings, base_directory
        - test: reload settings on change


    @version 0.2.7
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
from FuzzyFilePath.query import Query
from FuzzyFilePath.query import Completion

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

    def get_filepath_completions(view, project_folder, current_folder):
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

        if Query.build(expression.get("needle"), trigger, current_folder) is False:
            # query is valid, but may not be triggered: not forced, no auto-options
            verbose(ID, "abort valid query: auto trigger disabled")
            return False

        verbose(ID, ".───────────────────────────────────────────────────────────────")
        verbose(ID, "| scope settings: {0}".format(trigger))
        verbose(ID, "| search needle: '{0}'".format(Query.get_needle()))
        verbose(ID, "| in base path: '{0}'".format(Query.get_base_path()))

        FuzzyFilePath.start_expression = expression
        completions = ProjectManager.search_completions(
            Query.get_needle(),
            project_folder,
            Query.get_extensions(),
            Query.get_base_path()
        )

        if completions and len(completions[0]) > 0:
            Completion.start(Query.get_replacements())
            view.run_command('_enter_insert_mode') # vintageous
            log("| => {0} completions found".format(len(completions)))
        else:
            sublime.status_message("FFP no filepaths found for '" + Query.get_needle() + "'")
            Completion.stop()
            log("| => no valid files found for needle: {0}".format(Query.get_needle()))

        log("")

        Query.reset()
        return completions

    def update_inserted_filepath(view, post_remove):
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
