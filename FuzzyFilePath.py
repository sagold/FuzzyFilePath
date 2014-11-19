""" FuzzyFilePath
    Manages filepath autocompletions

    # tasks

        - support multiple folders

    # errors

    @version 0.0.9
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re
import os

import FuzzyFilePath.context as context
from FuzzyFilePath.Project.ProjectFiles import ProjectFiles
from FuzzyFilePath.Scope import Scope
from FuzzyFilePath.Query import Query
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config

query = Query()
project_files = None



def get_current_line(view):
    selection = view.sel()[0]
    position = selection.begin()
    line_region = view.line(position)
    return view.substr(line_region)

def get_path_at_cursor(view):
    """
        Return path at current cursor position.
        Either returns cleaned scope value or tries to find it by extracting current line. Retrieving path via scope is
        the prefered way, but requires a valid scope which is not always given (css: background-image: url();)
    """
    result = Scope.get_path(view)
    if result is False:
        result = context.get_path_at_cursor(view)
    verbose("path", "at cursor", result)
    return result

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
    path = get_path_at_cursor(view)
    # remove path query completely
    final_path = Completion.get_final_path(path[0])
    verbose("insert", "final path", final_path)
    # replace current query with final path
    view.run_command("ffp_replace_region", { "a": path[1].a, "b": path[1].b, "string": final_path })
    Completion.reset()



def query_completions(view, prefix, locations):
    if query.valid is False:
        return False

    # needle = context.get_path_at_cursor(view)[0]
    needle = get_path_at_cursor(view)[0]
    current_scope = view.scope_name(locations[0])

    if query.build(current_scope, needle, query.relative) is False:
        return None

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



def update_project_files(view):
    if project_files is not None:
        for folder in sublime.active_window().folders():
            if folder in view.file_name():
                project_files.update(folder, view.file_name())

def update_project_folders(view):
    file_name = view.file_name()
    folders = sublime.active_window().folders()

    if (project_files is None):
        query.valid = False
        return False

    if query.update(folders, file_name):
        project_files.add(query.project_folder)


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

    track_insert = {
        "active": False,
        "start_line": "",
        "end_line": "",
        "end_path": ""
    }

    def on_query_completions(self, view, prefix, locations):
        """ query filepath completion """
        # check if a completion may be inserted
        if self.track_insert["active"] is False:
            self.start_tracking(view)

        if (config["DISABLE_AUTOCOMPLETION"] is True):
            return None

        return query_completions(view, prefix, locations)


    def on_post_insert_completion(self, view, command_name):
        """ post filepath completion """
        if Completion.active is True:
            Completion.active = False
            cleanup_completion(view)


    def on_post_save_async(self, view):
        update_project_files(view)


    def on_activated(self, view):
        update_project_folders(view)


    def start_tracking(self, view, command_name=None):
        self.track_insert["active"] = True
        self.track_insert["start_line"] = get_current_line(view)
        self.track_insert["end_line"] = None
        # verbose("--> trigger", command_name, self.track_insert["start_line"])
        word_replaced = re.split("[./]", self.track_insert["start_line"]).pop()
        if (self.track_insert["start_line"] is not word_replaced):
            Completion.before = re.sub(re.escape(word_replaced) + "$", "", self.track_insert["start_line"])


    def finish_tracking(self, view, command_name=None):
        self.track_insert["active"] = False
        self.track_insert["end_line"] = get_current_line(view)
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


    def on_post_text_command(self, view, command_name, args):
        # check if a completion is inserted
        current_line = get_current_line(view) #context.get_line_at_cursor(view)[0]
        command_trigger = command_name in config["TRIGGER_ACTION"] and self.track_insert["start_line"] != current_line
        if command_trigger or command_name in config["INSERT_ACTION"]:
            self.finish_tracking(view, command_name)
            self.on_post_insert_completion(view, command_name)
