""" FuzzyFilePath
    Manages filepath autocompletions

    # possible tasks

        - use test-triggers like "graffin:" instead/additionally to scope-triggers

        - support multiple folders
        - Cursor Position after replacement:
            require("../../../../optimizer|cursor|")
            SHOULD BE:
            require("../../../../optimizer")|cursor|

    # bugs

        - $module does not trigger completions
        - reproduce: query completion with one valid entry throws an error
        -   > require("./validate");
            + insert_path (+ instant completion)
            > reqexports.validate");

    # errors

        14/10/27

            Traceback (most recent call last):
              File "/Applications/Sublime Text.app/Contents/MacOS/sublime_plugin.py", line 374, in on_text_command
                res = callback.on_text_command(v, name, args)
              File "/Users/Gott/Dropbox/Applications/SublimeText/Packages/FuzzyFilePath/FuzzyFilePath.py", line 180, in on_text_command
                Completion["before"] = re.sub(word_replaced + "$", "", path[0])
              File "X/re.py", line 170, in sub
              File "X/functools.py", line 258, in wrapper
              File "X/re.py", line 274, in _compile
              File "X/sre_compile.py", line 493, in compile
              File "X/sre_parse.py", line 729, in parse
            sre_constants.error: unbalanced parenthesis

    @version 0.0.8
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re
import os

import FuzzyFilePath.context as context
from FuzzyFilePath.Cache.ProjectFiles import ProjectFiles
from FuzzyFilePath.Query import Query
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config


ACTION = {
    "active": False,
    "start": "",
    "end": ""
}

def start(view, command_name=None):
    ACTION["active"] = True
    ACTION["line_at_start"] = context.get_line_at_cursor(view)[0]
    ACTION["end"] = None
    verbose("--> trigger", command_name, ACTION)

def stop(view, command_name=None):
    ACTION["active"] = False
    ACTION["end"] = context.get_line_at_cursor(view)[0]
    verbose("<-- insert", command_name, ACTION)

Completion = {

    "active": False,
    "before": None,
    "after": None,
    "onInsert": []
}

query = Query()
project_files = None


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


class InsertPathCommand(sublime_plugin.TextCommand):

    # triggers autocomplete
    def run(self, edit, type="default", replace_on_insert=[]):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        query.relative = type
        if len(replace_on_insert) > 0:
            verbose("insert path", "override replace", replace_on_insert)
            query.override_replace_on_insert(replace_on_insert)

        self.view.run_command('auto_complete', "insert")


class FuzzyFilePath(sublime_plugin.EventListener):

    def on_post_insert_completion(self, view, command_name):
        """ Sanitize inserted path by
            - replacing temporary variables (~$)
            - replacing query partials, like "../<inserted path>"
        """
        stop(view, command_name)
        if Completion["active"] is False:
            return None
        # replace current path (fragments) with selected path
        # i.e. ../../../file -> ../file
        path = context.get_path_at_cursor(view)
        if (Completion["before"] is None):
            Completion["before"] = "";

        Completion["active"] = False

        verbose("cleanup path", path, Completion)

        final_path = re.sub("^" + Completion["before"], "", path[0])
        # hack reverse
        # final_path = final_path.replace("_D011AR_", "$")
        final_path = re.sub(config["ESCAPE_DOLLAR"], "$", final_path)
        # modify result
        for replace in Completion["replaceOnInsert"]:
            final_path = re.sub(replace[0], replace[1], final_path)
        # cleanup path
        view.run_command("ffp_replace_region", { "a": path[1].a, "b": path[1].b, "string": final_path })
        #reset
        Completion["before"] = None
        Completion["replaceOnInsert"] = []

    def on_text_command(self, view, command_name, args):
        if command_name in config["TRIGGER_ACTION"] or command_name in config["INSERT_ACTION"]:
            start(view, command_name)
        elif command_name == "hide_auto_complete":
            Completion["active"] = False
            stop(view, command_name)
        # if command_name == "commit_completion":
        #     path = context.get_path_at_cursor(view)

        #     word_replaced = re.split("[./]", path[0]).pop()
        #     if (path is not word_replaced):
        #         Completion["before"] = re.sub(word_replaced + "$", "", path[0])


    def on_post_text_command(self, view, command_name, args):
        current_line = context.get_line_at_cursor(view)[0]
        insert = command_name in config["TRIGGER_ACTION"] and ACTION["line_at_start"] != current_line
        insert = insert or command_name in config["INSERT_ACTION"]

        if insert is True:
            self.on_post_insert_completion(view, command_name)

    def on_query_completions(self, view, prefix, locations):
        # auto complete on input
        if ACTION["active"] is False:
            start(view)

        if (config["DISABLE_AUTOCOMPLETION"] is True):
            return None

        if query.valid is False:
            return False

        needle = context.get_path_at_cursor(view)[0]
        current_scope = view.scope_name(locations[0])

        if query.build(current_scope, needle, query.relative) is False:
            return None

        # vintageous
        view.run_command('_enter_insert_mode')

        completions = project_files.search_completions(query.needle, query.project_folder, query.extensions, query.relative, query.extension)

        if len(completions) > 0:
            Completion["active"] = True
            verbose("query", "needle:", needle, "relative:", query.relative)
            verbose("query", "completions:", completions)
            Completion["replaceOnInsert"] = query.replace_on_insert

        else:
            Completion["active"] = False

        query.reset()
        return completions


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
