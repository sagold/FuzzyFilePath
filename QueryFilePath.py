###
# # QueryFilePath
#
# Manages autocompletions
#
# @version 0.0.2
# @author Sascha Goldhofer <post@saschagoldhofer.de>
###
import sublime
import sublime_plugin
import re
import os

from QueryFilePath.Cache.ProjectFiles import ProjectFiles

Completion = {

    "active": False,
    "before": None,
    "after": None
}

# @type {dict} query parameters and cache
Query = {

    "auto_trigger": False,

    "valid": False,
    "current_folder": None,
    "project_folder": None,
    "relative": False,
    "extension": True,
    "extensions": []
}
# @type {array} list of completion settings defined by scope
Scopes = None
# @type {ProjectFiles} project cache instance
project_files = None

##
# init
def plugin_loaded():
    settings = sublime.load_settings("QueryFilePath.sublime-settings")
    settings.add_on_change("extensionsToSuggest", update_settings)
    update_settings()

##
# reads plugin and project settings
def update_settings():
    global project_files, Scopes

    exclude_folders = []
    project_folders = sublime.active_window().project_data().get("folders", [])
    settings = sublime.load_settings("QueryFilePath.sublime-settings")
    Scopes = settings.get("scopes", [])

    Query["auto_trigger"] = settings.get("auto_trigger", True)

    # build exclude folders
    for folder in project_folders:
        base = folder.get("path")
        exclude = folder.get("folder_exclude_patterns", [])
        for f in exclude:
            exclude_folders.append(os.path.join(base, f))

    # or use default settings
    if (len(exclude_folders) == 0):
        exclude_folders = settings.get("excludeFolders", ["node_modules"])

    project_files = ProjectFiles(settings.get("extensionsToSuggest", ["js"]), exclude_folders)

##
# update current views folder in query
#
# @param {sublime.Window} view  current
def update_query(view):
    folders = sublime.active_window().folders()
    filename = view.file_name()

    Query["valid"] = is_valid(folders, filename)
    if Query["valid"] is False:
        return False

    project_folder = folders[0]
    Query["project_folder"] = project_folder

    current_folder = re.sub("/[^/]*$", "", filename)
    current_folder = re.sub(project_folder, "", current_folder)
    Query["current_folder"] = current_folder

    return True

def get_path_at_cursor(view):
    word = get_word_at_cursor(view)
    line = get_line_at_cursor(view)

    path = get_path(line[0], word[0])

    path_region = sublime.Region(word[1].a, word[1].b)
    path_region.b = word[1].b
    path_region.a = word[1].a - (len(path) - len(word[0]))
    # print("path", path, "region", path_region, "str", view.substr(path_region))

    return [path, path_region]

def get_path(line, word):
    path = None
    full_words = line.split(" ")

    for full_word in full_words:
        if word in line:
            if (path is not None):
                print("multiple matches found in", line, "for", word)
            path = extract_path_from(full_word, word)

    if (path is None):
        return word

    # ! (get &) return region of path
    return path


def extract_path_from(word, needle):
    result = re.search("([^\"\'\s]*)" + needle, word)

    if (result is not None):
        return result.group(0)


def get_line_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.line(position)

    return [view.substr(region), region]


def get_word_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.word(position)
    word = view.substr(region)

    # single line only
    if "\n" in word:
        return ["", sublime.Region(position, position)]

    if word[0] is '"':
        word = word[1:]
        region.a += 1

    if word[-1:] is '"':
        word = word[1:]
        region.a += 1

    return [word, region]


class ReplaceRegionCommand(sublime_plugin.TextCommand):

    def run(self, edit, a, b, string):
        self.view.replace(edit, sublime.Region(a, b), string)



def build_query(current_scope, needle, force_type=False):
    """ Setup properties for completion query

        Behaviour
        - replaces starting ./ with current folder
        - uses all extensions if completion is triggered and not specified in settings
        - triggers completion if
          - triggered manually
          - scope settings found and auto true OR
          - auto_trigger is set to true and input is path
        - inserts path relative if
          - set in settings and true OR if not false
          - path starts with ../ or ./
          - triggered manually (overrides all)

        Keyword arguments:
        current_scope -- complete scope on current cursor position
        needle -- path to search
        force_type -- "default", "relative", "absolute" (default False)
    """
    triggered = force_type is not False
    properties = get_properties(current_scope)
    query = evaluate_path(needle)

    if triggered is False and properties is False and query["is_path"] is False:
        return False

    Query["needle"] = query["needle"] # resolved needle for "./" or "../"
    Query["relative"] = query["relative"] # default current string
    Query["active"] = False # default
    Query["extensions"] = ["*"] # default

    if properties:
        Query["active"] = properties.get("auto", Query["auto_trigger"])
        Query["extension"] = properties.get("insertExtension", True)
        Query["extensions"] = properties.get("extensions", ["js"])
        Query["relative"] = properties.get("relative", query["relative"])

    # TEST: ignore property settings
    if query["is_path"]:
        Query["active"] = Query["auto_trigger"]

    if Query["relative"] is None:
        Query["relative"] = False

    if force_type is not False:
        Query["active"] = True

        if force_type is not "default":
            Query["relative"] = force_type == "relative"

    if Query["relative"] is True:
        Query["relative"] = Query["current_folder"]
    elif Query["relative"] is None:
        Query["relative"] = False

    return Query


def evaluate_path(needle):

    properties = {

        "is_path": False,
        "relative": False,
        "needle": needle
    }

    if needle.startswith("./"):
        properties["is_path"] = True
        properties["relative"] = Query["current_folder"]
        properties["needle"] = needle.replace("./", Query["current_folder"])

    elif needle.startswith("../"):
        properties["is_path"] = True
        properties["relative"] = Query["current_folder"]
        properties["needle"] = needle.replace("../", "")

    elif re.search("^\/[A-Za-z0-9\_\-\s\.]*\/", needle):
        properties["is_path"] = True
        properties["relative"] = False
        properties["needle"] = needle

    return properties


def get_properties(current_scope):

    for properties in Scopes:
        scope = properties.get("scope").replace("//", "")
        if re.search(scope, current_scope):
            return properties

    return False

##
# trigger autocomplete popup
#
# @extends sublime_plugin.TextCommand
class InsertPathCommand(sublime_plugin.TextCommand):

    def run(self, edit, type="default"):
        global Query
        Query["relative"] = type
        view = sublime.active_window().active_view()
        view.run_command('auto_complete')

##
# query autocomplete request
#
# @extends sublime_plugin.EventListener
class QueryFilePath(sublime_plugin.EventListener):

    def on_text_command(self, view, command_name, args):
        global Completion

        if command_name == "commit_completion":
            path = get_path_at_cursor(view)
            word_replaced = re.split("[./]", path[0]).pop()

            if (path is not word_replaced):
                Completion["before"] = re.sub(word_replaced + "$", "", path[0])
                # print("before commit", path[0], word_replaced, Completion["before"])

        elif command_name == "hide_auto_complete":
            Completion["active"] = False

    def on_post_text_command(self, view, command_name, args):
        global Completion

        if (command_name == "commit_completion" and Completion["active"] is True):

            Completion["active"] = False
            if Completion["before"] is not None:

                path = get_path_at_cursor(view)
                final_path = re.sub("^" + Completion["before"], "", path[0])
                Completion["before"] = None
                # print("replace", path[0], "with", Completion["before"], final_path)
                view.run_command("replace_region", { "a": path[1].a, "b": path[1].b, "string": final_path })


    def on_post_save_async(self, view):

        global project_files

        if project_files is not None:
            for folder in sublime.active_window().folders():
                if folder in view.file_name():
                    # print("__CompletePath__ project file saved")
                    project_files.update(folder, view.file_name())


    def on_query_completions(self, view, prefix, locations):

        global project_files, Query

        if (Query["valid"] is False):
            return False

        current_scope = view.scope_name(locations[0])
        needle = get_path_at_cursor(view)[0]
        query = build_query(current_scope, needle, Query["relative"])

        # evaluate
        if query["active"] is False:
            print("abort: query not activated", Query["relative"])
            return

        # go into insert mode (ignored if not available)
        view.run_command('_enter_insert_mode')
        # print("search", query["needle"], "relative to", query["relative"], "base path:")
        completions = project_files.search_completions(query["needle"], query["project_folder"], query["extensions"], query["relative"], query["extension"])

        if completions:
            Completion["active"] = True

        # reset query
        Query["relative"] = False
        Query["active"] = False
        Query["extension"] = True

        return completions

    def on_activated(self, view):

        global project_files
        global Query

        if (project_files is None or view.file_name() is None):
            Query["valid"] = False
            return False

        if update_query(view):
            project_files.add(Query["project_folder"])

##
# validate current project-files
#
# @param {Array} folders    list of current project folders
# @param {String} filename  filepath and filename of current view
def is_valid(folders, filename):

    if (filename is None):
        # print("__QueryFilePath__ [A] filename is None")
        return False

    # single file?
    if (len(folders) == 0):
        # print("__QueryFilePath__ [A] no folders")
        return False

    # independent file?
    if (not folders[0] in filename):
        # print("__QueryFilePath__ [A] independent file")
        return False

    # multiple folders?
    if (len(folders) > 1):
        print("__QueryFilePath__ [W] multiple folders not yet supported")

    return True
