""" FuzzyFilePath
    Manages filepath autocompletions

    # tasks

        - support multiple folders

    # errors

        - @cleanup_completion: cleanup performs no cleanup

    @version 0.0.9
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re
import os

import FuzzyFilePath.context as context
from FuzzyFilePath.expression import Context
from FuzzyFilePath.Project.ProjectFiles import ProjectFiles
from FuzzyFilePath.Scope import Scope
from FuzzyFilePath.Query import Query
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config

query = Query()
project_files = None

class Selection:

    def get_position(view):
        return view.sel()[0].begin()

    def get_line(view):
        position = Selection.get_position(view)
        line_region = view.line(position)
        return view.substr(line_region)

    def get_scope(view):
        return view.scope_name(Selection.get_position(view))


class Completion:

    active = False
    before = None
    after = None
    onInsert = []

    def reset():
        Completion.before = None
        Completion.replaceOnInsert = []

    def get_final_path(path):
        if Completion.before is not None:
            Completion.before = re.escape(Completion.before)
            path = re.sub("^" + Completion.before, "", path)
            Completion.before = None

        print("build final path", path, "before", Completion.before, "to", path)

        # hack reverse
        path = re.sub(config["ESCAPE_DOLLAR"], "$", path)
        for replace in Completion.replaceOnInsert:
            path = re.sub(replace[0], replace[1], path)
        return path


def plugin_loaded():
    """ load settings """
    settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
    settings.add_on_change("extensionsToSuggest", update_settings)
    update_settings()


def update_settings():
    """ restart projectFiles with new plugin and project settings """
    global project_files, config

    exclude_folders = []
    project_folders = sublime.active_window().project_data().get("folders", [])
    settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
    query.scopes = settings.get("scopes", [])
    query.auto_trigger = (settings.get("auto_trigger", True))
    exclude_folders = settings.get("exclude_folders", ["node_modules"])
    project_files = ProjectFiles(settings.get("extensionsToSuggest", ["js"]), exclude_folders)

    config["DISABLE_KEYMAP_ACTIONS"] = settings.get("disable_keymap_actions", config["DISABLE_KEYMAP_ACTIONS"]);
    config["DISABLE_AUTOCOMPLETION"] = settings.get("disable_autocompletions", config["DISABLE_AUTOCOMPLETION"]);
    config["DEBUG"] = settings.get("DEBUG", config["DEBUG"])



def cleanup_completion(view):
    expression = Context.get_context(view)
    # remove path query completely
    final_path = Completion.get_final_path(expression["needle"])
    verbose("insert", "final path", final_path)
    print("cleanup", expression, final_path)
    # replace current query with final path
    view.run_command("ffp_replace_region", { "a": expression["region"].a, "b": expression["region"].b, "string": final_path })
    Completion.reset()



def query_completions(view, prefix, locations):

    # parse current context
    expression = Context.get_context(view)
    if expression is False:
        # current context is not valid
        print("current context is not valid")
        return False

    # check if there is a trigger for the current expression
    current_scope = Selection.get_scope(view)
    trigger = Context.find_trigger(expression, current_scope)
    if trigger is False:
        print("no valid trigger for current expression", expression)
        return False

    if query.build(expression.get("needle"), trigger, query.relative) is False:
        # query is valid, but should not be triggered: not forced, no auto-options
        return False


    print("FFP QUERYING FILES")
    completions = project_files.search_completions(query.needle, query.project_folder, query.extensions, query.relative, query.extension)
    print("FFP QUERYING FILES DONE")


    if len(completions[0]) > 0:
        verbose("completions", len(completions[0]), "matches found for", query.needle)
        Completion.active = True
        Completion.replaceOnInsert = query.replace_on_insert
        # vintageous
        view.run_command('_enter_insert_mode')
    else:
        verbose("completions", "no completions for", query.needle)
        Completion.active = False

    query.reset()
    return completions



def file_in_project(filename, folders):
    if (filename is None):
        # print("__QueryFilePath__ [A] file has not yet been saved")
        return False
    if (len(folders) == 0):
        # print("__QueryFilePath__ [A] no project/folder")
        return False
    if (not folders[0] in filename):
        # print("__QueryFilePath__ [A] file not within project folders")
        return False
    if (len(folders) > 1):
        print("__QueryFilePath__ [W] multiple folders not yet supported")


class InsertPathCommand(sublime_plugin.TextCommand):
    """ trigger customized autocomplete """
    def run(self, edit, type="default", replace_on_insert=[]):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        query.relative = type
        if len(replace_on_insert) > 0:
            verbose("insert path", "override replace", replace_on_insert)
            query.override_replace_on_insert(replace_on_insert)

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


    def on_query_completions(self, view, prefix, locations):
        if self.track_insert["active"] is False:
            self.start_tracking(view)

        if config["DISABLE_AUTOCOMPLETION"] is False and self.is_project_file:
            return query_completions(view, prefix, locations)
        else:
            return False


    def on_post_insert_completion(self, view, command_name):
        if Completion.active is True:
            cleanup_completion(view)
        Completion.active = False


    # update project by file
    def on_post_save_async(self, view):
        if project_files is not None:
            folders = sublime.active_window().folders()
            match = [folder for folder in folders if folder in view.file_name()]
            if len(match) > 0:
                project_files.update(folder, view.file_name())


    # validate and update project folders
    def on_activated(self, view):
        file_name = view.file_name()
        folders = sublime.active_window().folders()

        # abort if file is not within a project
        self.is_project_file = file_in_project(file_name, folders)
        if not self.is_project_file:
            query.valid = False
            return False

        self.project_folder = folders[0]
        current_folder = os.path.dirname(file_name)
        current_folder = os.path.relpath(current_folder, project_folder)
        current_folder = "" if current_folder == "." else current_folder
        self.current_folder = posix(current_folder)

        project_files.add(self.project_folder)

    def start_tracking(self, view, command_name=None):
        self.track_insert["active"] = True
        self.track_insert["start_line"] = Selection.get_line(view)
        self.track_insert["end_line"] = None
        # verbose("--> trigger", command_name, self.track_insert["start_line"])
        word_replaced = re.split("[./]", self.track_insert["start_line"]).pop()
        if (self.track_insert["start_line"] is not word_replaced):
            Completion.before = re.sub(re.escape(word_replaced) + "$", "", self.track_insert["start_line"])


    def finish_tracking(self, view, command_name=None):
        self.track_insert["active"] = False
        self.track_insert["end_line"] = Selection.get_line(view)
        # verbose("<-- insert", command_name)


    def abort_tracking(self):
        self.track_insert["active"] = False


    def on_text_command(self, view, command_name, args):
        # check if a completion may be inserted
        if command_name in config["TRIGGER_ACTION"] or command_name in config["INSERT_ACTION"]:
            self.start_tracking(view, command_name)
        elif command_name == "hide_auto_complete":
            Completion.active = False
            self.abort_tracking()


    # check if a completion is inserted and trigger on_post_insert_completion
    def on_post_text_command(self, view, command_name, args):
        current_line = Selection.get_line(view)
        command_trigger = command_name in config["TRIGGER_ACTION"] and self.track_insert["start_line"] != current_line
        if command_trigger or command_name in config["INSERT_ACTION"]:
            self.finish_tracking(view, command_name)
            self.on_post_insert_completion(view, command_name)
