""" FuzzyFilePath - autocomplete filepaths

    # tasks

        - check windows, update sublime text 2
        - add to command palette: settings, base_directory
        - add force update cached folder

    @version 0.1.0-alpha
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re

from expression import Context
from project.project_files import ProjectFiles
from common.verbose import verbose
from common.verbose import log
from common.config import config
from common.selection import Selection
from common.path import Path

# from Cache.ProjectFiles import ProjectFiles
# from Query import Query

project_files = None
scope_cache = {}

def update_settings():
    """ restart projectFiles with new plugin and project settings """
    global project_files, scope_cache

    scope_cache.clear()
    settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])

    # st2 - has to check window
    project_settings = False
    current_window = sublime.active_window()
    if current_window:
        project_settings = current_window.active_view().settings().get('FuzzyFilePath', False)

    # sync settings to config
    for key in config:
        config[key] = settings.get(key.lower(), config[key])
    # mapping
    config["TRIGGER"] = settings.get("scopes", config["TRIGGER"])
    # merge project settings stored in "settings: { FuzzyFilePath: ..."
    if project_settings:
        # mapping
        config["TRIGGER"] = project_settings.get("scopes", config["TRIGGER"])
        for key in config:
            config[key] = project_settings.get(key.lower(), config[key])
    # build extensions to suggest
    extensionsToSuggest = []
    for scope in config["TRIGGER"]:
        ext = scope.get("extensions", [])
        extensionsToSuggest += ext
    # remove duplicates
    extensionsToSuggest = list(set(extensionsToSuggest))

    project_files = ProjectFiles()
    project_files.update_settings(extensionsToSuggest, config["EXCLUDE_FOLDERS"])
    # validate base_directory
    if config["BASE_DIRECTORY"]:
        config["BASE_DIRECTORY"] = Path.sanitize_base_directory(config["BASE_DIRECTORY"])

    log("logging enabled")
    log("project base directory set to '{0}'".format(config["BASE_DIRECTORY"]))
    log("{0} scope triggers loaded".format(len(config["TRIGGER"])))


""" load settings """
settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
settings.add_on_change("scopes", update_settings)
update_settings()


class Completion:
    """
        Manage active state of completion and post cleanup
    """
    active = False  # completion currently in progress (servce suggestions)
    onInsert = []   # substitutions for building final path
    base_directory = False  # base directory to set for absolute path, enabled by query...

    @staticmethod
    def start(post_replacements=[]):
        Completion.replaceOnInsert = post_replacements
        Completion.active = True

    @staticmethod
    def stop():
        Completion.active = False
        # set by query....
        Completion.base_directory = False

    @staticmethod
    def is_active():
        return Completion.active

    @staticmethod
    def get_final_path(path, post_remove):
        log("cleanup filepate: '{0}'".format(path))

        # string to replace on post_insert_completion
        post_remove = re.escape(post_remove)
        path = re.sub("^" + post_remove, "", path)
        # hack reverse
        path = re.sub(config["ESCAPE_DOLLAR"], "$", path)
        for replace in Completion.replaceOnInsert:
            path = re.sub(replace[0], replace[1], path)

        if Completion.base_directory and path.startswith("/"):
            path = re.sub("^\/" + Completion.base_directory, "", path)
            path = Path.sanitize(path)

        log("final filepate: '{0}'".format(path))
        return path


class InsertPathCommand(sublime_plugin.TextCommand):
    # trigger customized autocomplete
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

    @staticmethod
    def reset():
        Query.extensions = ["*"]
        Query.base_path = False
        Query.replace_on_insert = []
        Query.forces.clear()

    @staticmethod
    def force(key, value):
        Query.forces[key] = value

    @staticmethod
    def get(key, default=None):
        return Query.forces.get(key, default)

    @staticmethod
    def by_command():
        return bool(Query.get("filepath_type", False))

    @staticmethod
    def build(needle, trigger, current_folder, project_folder):
        force_type = Query.get("filepath_type", False)
        triggered = Query.by_command()
        filepath_type = "relative"
        needle = Path.sanitize(needle)
        needle_is_absolute = Path.is_absolute(needle)
        needle_is_relative = Path.is_relative(needle)
        needle_is_path = needle_is_absolute or needle_is_relative
        # abort if autocomplete is not available
        if not triggered and trigger.get("auto", False) is False and needle_is_path is False:
            # print("FFP no autocomplete")
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
        Query.extensions = trigger.get("extensions", ["*"])
        Query.extensions = Query.get("extensions", Query.extensions)
        Query.needle = Query.build_needle_query(needle, current_folder)
        log("\nfilepath type\n--------")
        log("type:", filepath_type)
        log("base_path:", Query.base_path)
        log("needle:", Query.needle)
        log("current folder", current_folder)
        return triggered or (config["AUTO_TRIGGER"] if needle_is_path else trigger.get("auto", config["AUTO_TRIGGER"]))

    @staticmethod
    def build_needle_query(needle, current_folder):
        current_folder = "" if not current_folder else current_folder
        needle = re.sub("\.\./", "", needle)
        needle = re.sub("[\\n\\t]", "", needle)
        needle = needle.strip()
        if needle.startswith("./"):
            needle = current_folder + re.sub("\.\/", "", needle)
        return needle


def cleanup_completion(view, post_remove):

    print("cleanup completion")

    expression = Context.get_context(view)
    # remove path query completely
    final_path = Completion.get_final_path(expression["needle"], post_remove)
    log("post cleanup path:'", expression.get("needle"), "' ~~> '", final_path, "'")
    # replace current query with final path
    view.run_command("ffp_replace_region", { "a": expression["region"].a, "b": expression["region"].b, "string": final_path })


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


def query_completions(view, project_folder, current_folder):
    global Context, Selection

    current_scope = Selection.get_scope(view)

    if not Query.by_command():
        triggers = get_matching_autotriggers(current_scope, config["TRIGGER"])
    else:
        triggers = config["TRIGGER"]

    if not bool(triggers):
        log("abort query, no valid scope-regex for current context")
        return False

    # parse current context, may contain 'is_valid: False'
    expression = Context.get_context(view)
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
        log("abort completion, no trigger found")
        return False

    if not expression["valid_needle"]:
        word = Selection.get_word(view)
        expression["needle"] = re.sub("[^\.A-Za-z0-9\-\_$]", "", word)
        log("changed invalid needle to {0}".format(expression["needle"]))
    else:
        log("context evaluation {0}".format(expression))

    if Query.build(expression.get("needle"), trigger, current_folder, project_folder) is False:
        # query is valid, but may not be triggered: not forced, no auto-options
        log("abort valid query: auto trigger disabled")
        return False

    if (config["LOG"]):
        log("")
        log("query completions:")
        log("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        log("scope settings: {0}".format(trigger))
        log("search needle: '{0}'".format(Query.needle))
        log("in base path: '{0}'".format(Query.base_path))

    completions = project_files.search_completions(Query.needle, project_folder, Query.extensions, Query.base_path)

    if completions and len(completions[0]) > 0:
        Completion.start(Query.replace_on_insert)
        view.run_command('_enter_insert_mode') # vintageous
        log("=> {0} completions found".format(len(completions)))
    else:
        sublime.status_message("FFP no filepaths found for '" + Query.needle + "'")
        Completion.stop()
        log("=> no valid files found for needle: {0}".format(Query.needle))

    log("")

    Query.reset()
    return completions


class FuzzyFilePath(sublime_plugin.EventListener):

    is_project_file = False,
    project_folder = False,
    current_folder = False,

    # tracks on_post_insert_completion
    track_insert = {
        "active": False,
        "start_line": "",
        "end_line": ""
    }

    post_remove = "",

    def on_query_completions(self, view, prefix, locations):
        if config["DISABLE_AUTOCOMPLETION"] and not Query.by_command():
            return False

        if self.track_insert["active"] is False:
            self.start_tracking(view)

        if self.is_project_file:
            return query_completions(view, self.project_folder, self.current_folder)
        else:
            verbose("disabled or not a project", self.is_project_file)
            return False

    def on_post_insert_completion(self, view, command_name):
        if Completion.is_active():
            cleanup_completion(view, self.post_remove)
            Completion.stop()


    # update project by file
    def on_post_save(self, view):
        if project_files is None:
            return False

        folders = sublime.active_window().folders()
        match = [folder for folder in folders if folder in view.file_name()]
        if len(match) > 0:
            return project_files.update(match[0], view.file_name())
        else:
            return False

    # validate and update project folders
    def on_activated(self, view):
        self.is_project_file = False
        self.project_folder = None

        current_window = sublime.active_window()
        if not current_window:
            return False

        file_name = view.file_name()
        folders = current_window.folders()

        if folders is None or file_name is None:
            return False

        for folder in folders:
            if folder in file_name:
                self.is_project_file = True
                self.project_folder = folder
        # abort if file is not within a project
        if not self.is_project_file:
            sublime.status_message("FFP abort. File is not within a project")
            return False
        # default to False fails for relative resolution from base_directory
        # but False is required for query of absolute path
        self.current_folder = Path.get_relative_folder(file_name, self.project_folder)

        if project_files:
            project_files.add(self.project_folder)


    # track post insert insertion
    def start_tracking(self, view, command_name=None):

        print("start tracking")

        self.track_insert["active"] = True
        self.track_insert["start_line"] = Selection.get_line(view)
        self.track_insert["end_line"] = None
        """
            - sublime inserts completions by replacing the current word
            - this results in wrong path insertions if the query contains word_separators like slashes
            - thus the path until current word has to be removed after insertion
        """
        needle = Context.get_context(view).get("needle")
        word = re.escape(Selection.get_word(view))
        self.post_remove = re.sub(word + "$", "", needle)
        verbose("cleanup", "remove:", self.post_remove, "of", needle)

    def finish_tracking(self, view, command_name=None):

        print("finish tracking")

        self.track_insert["active"] = False
        self.track_insert["end_line"] = Selection.get_line(view)

    def abort_tracking(self):

        print("abort tracking")

        self.track_insert["active"] = False

    def on_text_command(self, view, command_name, args):

        print("\t\ttext command: " + command_name)

        # check if a completion may be inserted
        if command_name in config["TRIGGER_ACTION"] or command_name in config["INSERT_ACTION"]:
            self.start_tracking(view, command_name)
            print("on text command", command_name)

        elif command_name == "hide_auto_complete":
            Completion.stop()
            self.abort_tracking()
            print("on text command", command_name)

    # check if a completion is inserted and trigger on_post_insert_completion
    # def on_post_text_command(self, view, command_name, args):
    #     current_line = Selection.get_line(view)
    #     command_trigger = command_name in config["TRIGGER_ACTION"] and self.track_insert["start_line"] != current_line
    #     if command_trigger or command_name in config["INSERT_ACTION"]:
    #         self.finish_tracking(view, command_name)
    #         self.on_post_insert_completion(view, command_name)
