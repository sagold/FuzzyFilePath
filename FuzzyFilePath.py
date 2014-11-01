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

import FuzzyFilePath.context
from FuzzyFilePath.Cache.ProjectFiles import ProjectFiles
from FuzzyFilePath.Query import Query
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config



TRIGGER_ACTION = ["auto_complete", "insert_path"]
INSERT_ACTION = ["commit_completion", "insert_best_completion"]
ACTION = {
    "active": False,
    "start": "",
    "end": ""
}

def start(view):
    ACTION["active"] = True
    ACTION["start"] = get_line_at_cursor(view)
    ACTION["end"] = None

def stop(view):
    ACTION["active"] = False
    ACTION["end"] = get_line_at_cursor(view)

DISABLE_AUTOCOMPLETION = False
DISABLE_KEYMAP_ACTIONS = False
FFP_SETTINGS_FILE = config["FFP_SETTINGS_FILE"]

Completion = {

    "active": 0,
    "before": None,
    "after": None,
    "onInsert": []
}

query = Query()
project_files = None


def plugin_loaded():
    """load settings"""
    settings = sublime.load_settings(FFP_SETTINGS_FILE)
    settings.add_on_change("extensionsToSuggest", update_settings)
    update_settings()


def update_settings():
    """restart projectFiles with new plugin and project settings"""
    global project_files, DISABLE_AUTOCOMPLETION, DISABLE_KEYMAP_ACTIONS

    exclude_folders = []
    project_folders = sublime.active_window().project_data().get("folders", [])
    settings = sublime.load_settings(FFP_SETTINGS_FILE)
    query.scopes = settings.get("scopes", [])
    query.auto_trigger = (settings.get("auto_trigger", True))
    exclude_folders = settings.get("exclude_folders", ["node_modules"])
    project_files = ProjectFiles(settings.get("extensionsToSuggest", ["js"]), exclude_folders)
    DISABLE_KEYMAP_ACTIONS = settings.get("disable_keymap_actions", DISABLE_KEYMAP_ACTIONS);
    DISABLE_AUTOCOMPLETION = settings.get("disable_autocompletions", DISABLE_AUTOCOMPLETION);


def get_path_at_cursor(view):
    word = get_word_at_cursor(view)
    line = get_line_at_cursor(view)
    path = get_path(line[0], word[0])
    path_region = sublime.Region(word[1].a, word[1].b)
    path_region.b = word[1].b
    path_region.a = word[1].a - (len(path) - len(word[0]))
    verbose("view", "path_at_cursor", path, "word:", word, "line", line)
    return [path, path_region]


# tested
def get_path(line, word):
    #! returns first match
    if word is None or word is "":
        return word

    needle = re.escape(word)
    full_words = line.split(" ")
    for full_word in full_words:
        if word in line:
            path = extract_path_from(full_word, needle)
            if not path is None:
                return path

    return word


#! fails if needle occurs also before path (line)
def extract_path_from(word, needle):
    result = re.search('([^\"\'\s]*)' + needle + '([^\"\'\s]*)', word)
    if (result is not None):
        return result.group(0)
    return None


def get_line_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.line(position)
    line = view.substr(region)
    verbose("view", "line at cursor", line)
    return [line, region]


# tested
def get_word_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.word(position)
    word = view.substr(region)
    # validate
    valid = not re.sub("[\"\'\s\(\)]*", "", word).strip() == ""
    if not valid:
        verbose("view", "invalid word", word)
        return ["", sublime.Region(position, position)]
    # single line only
    if "\n" in word:
        return ["", sublime.Region(position, position)]
    # strip quotes
    if len(word) > 0:
        if word[0] is '"':
            word = word[1:]
            region.a += 1

        if word[-1:] is '"':
            word = word[1:]
            region.a += 1
    # cleanup in case an empty string is encounterd
    if word.find("''") != -1 or word.find('""') != -1 or word.isspace():
        word = ""
        region = sublime.Region(position, position)

    return [word, region]


class ReplaceRegionCommand(sublime_plugin.TextCommand):
    # helper: replaces range with string
    def run(self, edit, a, b, string):
        if DISABLE_KEYMAP_ACTIONS is True:
            return False
        self.view.replace(edit, sublime.Region(a, b), string)


class InsertPathCommand(sublime_plugin.TextCommand):
    # triggers autocomplete
    def run(self, edit, type="default", replace_on_insert=[]):
        if DISABLE_KEYMAP_ACTIONS is True:
            return False

        query.relative = type
        if len(replace_on_insert) > 0:
            verbose("insert path", "override replace", replace_on_insert)
            query.override_replace_on_insert(replace_on_insert)

        self.view.run_command('auto_complete', "insert")


CLEANUP_COMMANDS = ["commit_completion", "insert_best_completion", "insert_path", "auto_complete"]


class FuzzyFilePath(sublime_plugin.EventListener):

    def on_text_command(self, view, command_name, args):

        if command_name in TRIGGER_ACTION:
            start(view)
            print("--> trigger", command_name, ACTION, args)

        elif command_name in INSERT_ACTION:
            # may already be started
            #     - insert_path & any in INSERT_ACTION
            #     - auto_complete & any in INSERT_ACTION
            start(view)
            print("--> insert", command_name, ACTION, args)

        if command_name == "commit_completion":
            path = get_path_at_cursor(view)

            word_replaced = re.split("[./]", path[0]).pop()
            if (path is not word_replaced):
                Completion["before"] = re.sub(word_replaced + "$", "", path[0])

        elif command_name == "hide_auto_complete":
            Completion["active"] = 0


    def on_post_text_command(self, view, command_name, args):
        insert = False

        if command_name in TRIGGER_ACTION:

            ACTION["end"] = get_line_at_cursor(view)

            if ACTION["start"] != ACTION["end"]:
                insert = True
                stop(view)
                print("<-- trigger", command_name, ACTION, args)

        elif command_name in INSERT_ACTION:
            insert = True
            stop(view)
            print("<-- insert", command_name, ACTION, args)


        if insert is True and Completion["active"] > 0: # Completion["active"] and
            """
                Sanitize inserted path by
                    - replacing temporary variables (_D011AR_ = $)
                    - replacing query partials, like "../<inserted path>"

                Major Problems when not checking on Completion["active] == True
                    - file path insertion not yet tracked. Since completions may be inserted
                        directly (without a manual selection), correct situation not yet retrieved
                    - this leads to weird insertions if working on non-paths and minor performance issues

                Problems checking on Completion["active"] == True
                    - misses direct insertions (auto_complete, insert_path). Thus workarounds like _D011AR_
                        remain in text

                INFO

                    shortcut
                       1. ON_POST_TEXT_COMMAND insert_path
                       2. QUERY COMPLETIONS
                       3. <select> + <enter>
                       4. ON_TEXT_COMMAND commit_completion / insert_best_completion (tab)
                       5. ON_POST_TEXT_COMMAND commit_completion / insert_best_completion (tab)
                       -

                    shortcut, single suggestion
                        1. ON_POST_TEXT_COMMAND insert_path
                        -

                    auto_complete
                        1. ON_POST_TEXT_COMMAND auto_complete
                        2. <select> + <enter>
                        3. ON_TEXT_COMMAND commit_completion / insert_best_completion (tab)
                        4. ON_POST_TEXT_COMMAND commit_completion / insert_best_completion (tab)
                        -
            """

            # replace current path (fragments) with selected path
            # i.e. ../../../file -> ../file
            path = get_path_at_cursor(view)
            if (Completion["before"] is None):
                Completion["before"] = "";

            Completion["active"] -= 1

            verbose("cleanup path", path, Completion)

            final_path = re.sub("^" + Completion["before"], "", path[0])
            # hack reverse
            # final_path = final_path.replace("_D011AR_", "$")
            final_path = re.sub(config["ESCAPE_DOLLAR"], "$", final_path)
            # modify result
            for replace in Completion["replaceOnInsert"]:
                final_path = re.sub(replace[0], replace[1], final_path)
            # cleanup path
            view.run_command("replace_region", { "a": path[1].a, "b": path[1].b, "string": final_path })
            #reset
            Completion["before"] = None
            Completion["replaceOnInsert"] = []





    def on_query_completions(self, view, prefix, locations):
        # auto complete on input
        if ACTION["active"] is False:
            start(view)
            print("--> auto", prefix, ACTION)

        if (DISABLE_AUTOCOMPLETION is True):
            return None

        if query.valid is False:
            return False

        needle = get_path_at_cursor(view)[0]
        current_scope = view.scope_name(locations[0])

        if query.build(current_scope, needle, query.relative) is False:
            return None

        # vintageous
        view.run_command('_enter_insert_mode')

        completions = project_files.search_completions(query.needle, query.project_folder, query.extensions, query.relative, query.extension)

        if len(completions) > 0:
            Completion["active"] = 2
            verbose("query", "needle:", needle, "relative:", query.relative)
            verbose("query", "completions:", completions)
            Completion["replaceOnInsert"] = query.replace_on_insert

        else:
            Completion["active"] = 0

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
