""" FuzzyFilePath
    Manages filepath autocompletions

    # CURRENT TASK

            fix get_path_at_cursor
            - may still return wrong needle position
            - validate string in current scope first
            - then try extending current region until complete path is found
                (instead of searching needle in line which may match wrong position)

    # possible tasks

        - use test-triggers like "graffin:" instead/additionally to scope-triggers
        - support multiple folders
        - Cursor Position after replacement:
            require("../../../../optimizer|cursor|")
            SHOULD BE:
            require("../../../../optimizer")|cursor|

    # bugs

        - long idle time
            - for multi cursor in paths (~> do not query anything!)
            - ???

    # errors

    @version 0.0.9
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re
import os

import FuzzyFilePath.context as context
from FuzzyFilePath.Cache.ProjectFiles import ProjectFiles
from FuzzyFilePath.Scope import Scope
from FuzzyFilePath.Query import Query
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config

query = Query()
project_files = None


def get_path_at_cursor(view):
    """
        Return path at current cursor position.
        Either returns cleaned scope value or tries to find it by extracting current line. Retrieving path via scope is
        the prefered way, but requires a valid scope which is not always given (css: background-image: url();)
    """
    result = Scope.get_path(view)
    if result is False:
        # prone to errors, see CURRENT TASK
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
        # hack reverse
        path = re.sub(config["ESCAPE_DOLLAR"], "$", path)
        for replace in Completion.replaceOnInsert:
            path = re.sub(replace[0], replace[1], path)
        return path


def plugin_loaded():
    """load settings"""
    settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
    settings.add_on_change("extensionsToSuggest", update_settings)
    update_settings()


def update_settings():
    """restart projectFiles with new plugin and project settings"""
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


class InsertPathCommand(sublime_plugin.TextCommand):
    """
        trigger customized autocomplete
    """
    def run(self, edit, type="default", replace_on_insert=[]):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        query.relative = type
        if len(replace_on_insert) > 0:
            verbose("insert path", "override replace", replace_on_insert)
            query.override_replace_on_insert(replace_on_insert)

        self.view.run_command('auto_complete', "insert")


class FuzzyFilePath(sublime_plugin.EventListener):
    """
        track and validate custom event: on_post_insert_completion
    """
    track_insert = {
        "active": False,
        "start_line": "",
        "start_path": "",
        "end_line": "",
        "end_path": ""
    }

    def start_tracking(self, view, command_name=None):
        self.track_insert["active"] = True
        self.track_insert["start_line"] = context.get_line_at_cursor(view)[0]
        self.track_insert["end_line"] = None
        self.track_insert["start_path"] = get_path_at_cursor(view)
        verbose("--> trigger", command_name, self.track_insert["start_line"], self.track_insert["start_path"])

        path = get_path_at_cursor(view)
        word_replaced = re.split("[./]", path[0]).pop()
        if (path is not word_replaced):
            Completion.before = re.sub(re.escape(word_replaced) + "$", "", path[0])

    def finish_tracking(self, view, command_name=None):
        self.track_insert["active"] = False
        self.track_insert["end_line"] = context.get_line_at_cursor(view)[0]
        self.track_insert["end_path"] = get_path_at_cursor(view)
        verbose("<-- insert", command_name, self.track_insert["end_path"])

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
        current_line = context.get_line_at_cursor(view)[0]
        insert = command_name in config["TRIGGER_ACTION"] and self.track_insert["start_line"] != current_line
        insert = insert or command_name in config["INSERT_ACTION"]

        if insert is True:
            self.finish_tracking(view, command_name)
            self.on_post_insert_completion(view, command_name)

    """
        query filepath completion
    """
    def on_query_completions(self, view, prefix, locations):
        # check if a completion may be inserted
        if self.track_insert["active"] is False:
            self.start_tracking(view)

        if (config["DISABLE_AUTOCOMPLETION"] is True):
            return None

        if query.valid is False:
            return False

        # needle = context.get_path_at_cursor(view)[0]
        needle = get_path_at_cursor(view)[0]
        current_scope = view.scope_name(locations[0])

        if query.build(current_scope, needle, query.relative) is False:
            return None

        completions = project_files.search_completions(query.needle, query.project_folder, query.extensions, query.relative, query.extension)

        if len(completions[0]) > 0:
            verbose("completions", len(completions[0]), "matches found for", query.needle, completions[0])
            Completion.active = True
            Completion.replaceOnInsert = query.replace_on_insert
            # vintageous
            view.run_command('_enter_insert_mode')
        else:
            verbose("completions", "no completions for", query.needle)
            Completion.active = False

        query.reset()
        return completions

    """
        post filepath completion
    """
    def on_post_insert_completion(self, view, command_name):
        """ Sanitize inserted path by
            - replacing temporary variables (~$)
            - replacing query partials, like "../<inserted path>"
        """
        if Completion.active is False:
            return None

        Completion.active = False
        path = get_path_at_cursor(view)
        # remove path query completely
        final_path = Completion.get_final_path(path[0])
        # replace current query with final path
        view.run_command("ffp_replace_region", { "a": path[1].a, "b": path[1].b, "string": final_path })

        Completion.reset()

    """
        update cached files
    """
    def on_post_save_async(self, view):
        if project_files is not None:
            for folder in sublime.active_window().folders():
                if folder in view.file_name():
                    project_files.update(folder, view.file_name())

    def on_activated(self, view):
        file_name = view.file_name()
        folders = sublime.active_window().folders()

        if (project_files is None):
            query.valid = False
            return False

        if query.update(folders, file_name):
            project_files.add(query.project_folder)
