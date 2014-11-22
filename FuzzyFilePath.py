""" FuzzyFilePath
    Manages filepath autocompletions

    # tasks

        - project-directory !

    # errors

    @version 0.0.9
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re
import os

from FuzzyFilePath.expression import Context
from FuzzyFilePath.project.project_files import ProjectFiles
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config
from FuzzyFilePath.common.selection import Selection
from FuzzyFilePath.common.path import Path

project_files = None

def plugin_loaded():
    """ load settings """
    settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
    settings.add_on_change("extensionsToSuggest", update_settings)
    update_settings()


def update_settings():
    """ restart projectFiles with new plugin and project settings """
    global project_files

    settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
    # update cache settings
    exclude_folders = settings.get("exclude_folders", ["node_modules"])
    project_files = ProjectFiles()
    project_files.update_settings(settings.get("extensionsToSuggest", ["js"]), exclude_folders)
    # sync settings to config
    for key in config:
        config[key] = settings.get(key.lower(), config[key])
    # mapping
    config["TRIGGER"] = settings.get("scopes", config["TRIGGER"])


class Completion:
    """
        Manage active state of completion and post cleanup
    """
    active = False  # completion currently in progress (servce suggestions)
    onInsert = []   # substitutions for building final path

    def start(post_replacements=[]):
        Completion.replaceOnInsert = post_replacements
        Completion.active = True

    def stop():
        Completion.active = False

    def is_active():
        return Completion.active

    def get_final_path(path, post_remove):
        # string to replace on post_insert_completion
        post_remove = re.escape(post_remove)
        path = re.sub("^" + post_remove, "", path)
        # hack reverse
        path = re.sub(config["ESCAPE_DOLLAR"], "$", path)
        for replace in Completion.replaceOnInsert:
            path = re.sub(replace[0], replace[1], path)

        return path


class Query:
    """
        Build current query based on received modifiers
    """
    extensions = ["*"]
    base_path = False
    replace_on_insert = []
    skip_update_replace = False

    def reset():
        Query.extensions = ["*"]
        Query.base_path = False
        Query.replace_on_insert = []
        Query.skip_update_replace = False

    def build(needle, properties, current_folder, project_folder, force_type=False):

        triggered = force_type is not False

        needle = Path.sanitize(needle)
        needle_is_absolute = Path.is_absolute(needle)
        needle_is_relative = Path.is_relative(needle)
        needle_is_path = needle_is_absolute or needle_is_relative

        # abort if autocomplete is not available
        if triggered is False and properties["auto"] is False and needle_is_path is False:
            return False

        # test path to trigger auto-completion by needle
        if triggered is False and properties["auto"] is False and config["AUTO_TRIGGER"] and needle_is_absolute:
            force_type = "absolute"

        # determine needle folder
        needle_folder = current_folder if needle_is_relative else False
        needle_folder = properties.get("relative", needle_folder)

        # print("triggered", triggered)
        # print("auto?", properties["auto"])
        # print("current folder", current_folder)
        # print("needle relative:", needle_is_relative)
        # print("needle absolute:", needle_is_absolute)
        # print("needle folder", needle_folder)

        # add evaluation to object
        Query.replace_on_insert = Query.replace_on_insert if Query.skip_update_replace else properties.get("replace_on_insert", [])
        Query.base_path = Query.get_path_type(needle_folder, current_folder, force_type)
        Query.needle = Query.build_needle_query(needle, current_folder)
        Query.extensions = properties.get("extensions", ["js"])
        # return trigger search
        return triggered or (config["AUTO_TRIGGER"] if needle_is_path else properties.get("auto", config["AUTO_TRIGGER"]))

    def build_needle_query(needle, current_folder):
        current_folder = "" if not current_folder else current_folder
        needle = re.sub("\.\./", "", needle)
        if needle.startswith("./"):
            needle = current_folder + re.sub("\.\/", "", needle)
        return needle

    def get_path_type(relative, current_folder, force_type=False):
        if force_type == "absolute":
            return False
        elif force_type == "relative":
            return current_folder

        if relative is None:
            return False
        elif relative is True:
            return current_folder


    def override_replace_on_insert(replacements):
        Query.replace_on_insert = replacements
        Query.skip_update_replace = True


def cleanup_completion(view, post_remove):
    expression = Context.get_context(view)
    # remove path query completely
    final_path = Completion.get_final_path(expression["needle"], post_remove)
    verbose("cleanup", "expression", expression.get("needle"), " -> ", final_path)
    # replace current query with final path
    view.run_command("ffp_replace_region", { "a": expression["region"].a, "b": expression["region"].b, "string": final_path })


def query_completions(view, project_folder, current_folder):
    global Context, Selection

    # parse current context, may contain 'is_valid: False'
    expression = Context.get_context(view)
    # check if there is a trigger for the current expression
    current_scope = Selection.get_scope(view)
    trigger = Context.find_trigger(expression, current_scope)

    print("expression", expression)

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
        return False

    if not expression["valid_needle"]:
        word = Selection.get_word(view)
        # print("INVALID NEEDLE", expression["needle"], "maybe?", re.sub("[^\.A-Za-z0-9\-\_$]", "", word))
        expression["needle"] = re.sub("[^\.A-Za-z0-9\-\_$]", "", word)

    # if expression["is_valid"] is False and Query.base_path is False:
    #     return False

    if Query.build(expression.get("needle"), trigger, current_folder, project_folder, Query.base_path) is False:
        # query is valid, but may not be triggered: not forced, no auto-options
        return False

    print("QUERY", Query.needle, "project: '", project_folder, "' relative: '", Query.base_path, "'")
    completions = project_files.search_completions(Query.needle, project_folder, Query.extensions, Query.base_path)
    print("completions", completions)

    if completions and len(completions[0]) > 0:
        Completion.start(Query.replace_on_insert)
        view.run_command('_enter_insert_mode') # vintageous
    else:
        sublime.status_message("FFP no completions found for '" + Query.needle + "'")
        Completion.stop()

    Query.reset()
    return completions


class InsertPathCommand(sublime_plugin.TextCommand):
    # trigger customized autocomplete
    def run(self, edit, type="default", replace_on_insert=[]):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        Query.base_path = type
        if len(replace_on_insert) > 0:
            verbose("insert path", "override replace", replace_on_insert)
            Query.override_replace_on_insert(replace_on_insert)

        self.view.run_command('auto_complete', "insert")


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
        if self.track_insert["active"] is False:
            self.start_tracking(view)

        if config["DISABLE_AUTOCOMPLETION"] is False and self.is_project_file:
            return query_completions(view, self.project_folder, self.current_folder)
        else:
            verbose("disabled or not a project", self.is_project_file)
            return False

    def on_post_insert_completion(self, view, command_name):
        if Completion.is_active():
            cleanup_completion(view, self.post_remove)
            Completion.stop()


    # update project by file
    def on_post_save_async(self, view):
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
        file_name = view.file_name()
        folders = sublime.active_window().folders()

        self.is_project_file = False
        self.project_folder = None

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
        self.track_insert["active"] = False
        self.track_insert["end_line"] = Selection.get_line(view)

    def abort_tracking(self):
        self.track_insert["active"] = False

    def on_text_command(self, view, command_name, args):
        # check if a completion may be inserted
        if command_name in config["TRIGGER_ACTION"] or command_name in config["INSERT_ACTION"]:
            self.start_tracking(view, command_name)
        elif command_name == "hide_auto_complete":
            Completion.stop()
            self.abort_tracking()

    # check if a completion is inserted and trigger on_post_insert_completion
    def on_post_text_command(self, view, command_name, args):
        current_line = Selection.get_line(view)
        command_trigger = command_name in config["TRIGGER_ACTION"] and self.track_insert["start_line"] != current_line
        if command_trigger or command_name in config["INSERT_ACTION"]:
            self.finish_tracking(view, command_name)
            self.on_post_insert_completion(view, command_name)
