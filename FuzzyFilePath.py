""" FuzzyFilePath
    Manages filepath autocompletions

    # possible tasks

        - use test-triggers like "graffin:" instead/additionally to scope-triggers

        - support multiple folders
        - Cursor Position after replacement:
            require("../../../../optimizer|cursor|")
            SHOULD BE:
            require("../../../../optimizer")|cursor|

    @version 0.0.7
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime
import sublime_plugin
import re
import os

from Cache.ProjectFiles import ProjectFiles
from Query import Query

DEBUG = False
DISABLE_AUTOCOMPLETION = False
DISABLE_KEYMAP_ACTIONS = False
def verbose(*args):
    if DEBUG is True:
        print(*args)

Completion = {

    "active": False,
    "before": None,
    "after": None,
    "onInsert": []
}

query = Query()
project_files = None


def update_settings():
    """restart projectFiles with new plugin and project settings"""
    global project_files, DISABLE_AUTOCOMPLETION, DISABLE_KEYMAP_ACTIONS

    exclude_folders = []
    # project_folders = sublime.active_window().project_data().get("folders", [])
    settings = sublime.load_settings("FuzzyFilePath.sublime-settings")
    query.scopes = settings.get("scopes", [])
    query.auto_trigger = (settings.get("auto_trigger", True))
    DISABLE_AUTOCOMPLETION = settings.get("disable_autocompletions", False);
    DISABLE_KEYMAP_ACTIONS = settings.get("disable_keymap_actions", False);

    # build exclude folders
    # for folder in project_folders:
    #     base = folder.get("path")
    #     exclude = folder.get("folder_exclude_patterns", [])
    #     for f in exclude:
    #         exclude_folders.append(os.path.join(base, f))
    # use default settings
    if (len(exclude_folders) == 0):
        exclude_folders = settings.get("excludeFolders", ["node_modules"])

    project_files = ProjectFiles(settings.get("extensionsToSuggest", ["js"]), exclude_folders)


# load settings
settings = sublime.load_settings("FuzzyFilePath.sublime-settings")
settings.add_on_change("extensionsToSuggest", update_settings)
update_settings()


def get_path_at_cursor(view):
    word = get_word_at_cursor(view)
    line = get_line_at_cursor(view)
    path = get_path(line[0], word[0])
    path_region = sublime.Region(word[1].a, word[1].b)
    path_region.b = word[1].b
    path_region.a = word[1].a - (len(path) - len(word[0]))
    verbose("path_at_cursor", path, "word:", word, "line", line)
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
    verbose("line at cursor", line)
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
        verbose("invalid word", word)
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
        self.view.run_command('auto_complete')


class FuzzyFilePath(sublime_plugin.EventListener):

    def on_text_command(self, view, command_name, args):
        if command_name == "commit_completion":
            path = get_path_at_cursor(view)
            word_replaced = re.split("[./]", path[0]).pop()
            if (path is not word_replaced):
                Completion["before"] = re.sub(word_replaced + "$", "", path[0])

        elif command_name == "hide_auto_complete":
            Completion["active"] = False


    def on_post_text_command(self, view, command_name, args):
        if (command_name == "commit_completion" and Completion["active"]):
            Completion["active"] = False
            # replace current path (fragments) with selected path
            # i.e. ../../../file -> ../file
            # if Completion["before"] is not None:
            path = get_path_at_cursor(view)
            final_path = re.sub("^" + Completion["before"], "", path[0])
            # hack reverse
            # final_path = final_path.replace("_D011AR_", "$")
            final_path = re.sub("_D011AR_", "$", final_path)
            # modify result
            for replace in Completion["replaceOnInsert"]:
                final_path = re.sub(replace[0], replace[1], final_path)
            # cleanup path
            view.run_command("replace_region", { "a": path[1].a, "b": path[1].b, "string": final_path })
            #reset
            Completion["before"] = None
            Completion["replaceOnInsert"] = []


    def on_post_save_async(self, view):
        if project_files is not None:
            for folder in sublime.active_window().folders():
                if folder in view.file_name():
                    project_files.update(folder, view.file_name())


    def on_query_completions(self, view, prefix, locations):
        if (DISABLE_AUTOCOMPLETION is True):
            return None

        if query.valid is False:
            return False

        needle = get_path_at_cursor(view)[0]
        current_scope = view.scope_name(locations[0])

        if query.build(current_scope, needle, query.relative) is False:
            return None

        view.run_command('_enter_insert_mode') # vintageous
        Completion["active"] = True
        completions = project_files.search_completions(query.needle, query.project_folder, query.extensions, query.relative, query.extension)
        verbose("query needle:", needle, "relative:", query.relative)
        verbose("query completions:", completions)
        Completion["replaceOnInsert"] = query.replace_on_insert
        query.reset()
        return completions


    def on_activated(self, view):
        file_name = view.file_name()
        current = sublime.active_window()

        if current is None:
            print("FFP: no active window")
            return False

        folders = current.folders()

        if (project_files is None):
            query.valid = False
            return False

        if query.update(folders, file_name):
            project_files.add(query.project_folder)
