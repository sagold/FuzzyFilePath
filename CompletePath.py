###
# # NodeJs require path completion
#
# Suggests and completes filename in require statement. Requires scope
# of require to be "require string".
#
# ## Usage
#
# - within require("") do not use / or .
#
# ## Missing features
#
# - MAJOR PERFORMANCE ISSUES??
# - optimize
#   - presplit filextension
# - completions not showing on single quotes: '...'
# - vim command does not insert
# - cleanup completions (no js, file type hint: json/js/folder)
# - exclude files and folders
# - extend base (project) path via project setting
# - include folders, [filetypes]
# - update files CACHE in/when x
# - replace special characters on insert (./)
#
# @version 0.0.1
# @updated 14/05/02
# @author Sascha Goldhofer <post@saschagoldhofer.de>
###
import sublime
import sublime_plugin
import os
import re

# Caches files (value) in parent_folder (key)
CACHE = {};
# options
REQUIRE = True
RELATIVE = True
COMPLETE = False


# class Cache:

#     def get_files(project_folder):




# PRINTS A SELECTION LIST
# self.view.show_popup_menu(["12", "123", "34redsas"], printDone)

class Insert_path(sublime_plugin.WindowCommand):

    def run(self, relative):

        global REQUIRE
        global RELATIVE
        global COMPLETE

        # self.path_relative = relative
        # self.path_require = False
        # self.show_completions = True

        REQUIRE = False
        RELATIVE = relative
        COMPLETE = True

        view = sublime.active_window().active_view()

        view.run_command('_enter_insert_mode')
        view.run_command('auto_complete')


class Insert_file_path(sublime_plugin.EventListener):

    # Checked once on activate
    valid = False
    project_folder = ""
    current_folder = ""
    # Folders to ignore when scanning for files
    ignore_folders = ["node_modules"]

    # build completions
    def on_query_completions(self, view, prefix, locations):

        global REQUIRE
        global RELATIVE
        global COMPLETE
        global CACHE

        if (self.valid is False):
            return False

        current_scope = view.scope_name(locations[0])

        # if (REQUIRE is False and re.search("require.*string", current_scope) is None):
        #     return False

        # only within strings
        if (not "string" in current_scope):
            print("aborting")
            return False

        if (re.search("require.*string", current_scope)):
            RELATIVE = True
            REQUIRE = True
        # not, if not triggered
        elif (COMPLETE is False):
            return False

        COMPLETE = False

        scope_region = view.extract_scope(locations[0])
        current_path = view.substr(scope_region)

        return get_completions(CACHE.get(self.project_folder), self.current_folder, current_path)

    # sets files CACHE on window activation
    def on_activated(self, view):

        global CACHE

        window = sublime.active_window()
        folders = window.folders()
        file = view.file_name()

        self.valid = not abort(folders, file)
        if (self.valid is False):
            print("__CompletePath__ file invalid")
            return

        self.project_folder = folders[0]
        self.current_folder = re.sub("/[^/]*$", "", file)
        self.current_folder = re.sub(self.project_folder, "", self.current_folder)

        if not self.project_folder in CACHE:
            files = get_js_files(self.project_folder, self.project_folder, self.ignore_folders)
            CACHE.update({self.project_folder: files})
            print("__CompletePath__ CACHE updated")


##
# Returns list of completions or False
#
# @param {Array} project_files
# @param {String} current_folder    of active window
# @param {String} needle            current require argument
def get_completions(project_files, current_folder, needle):

    global REQUIRE

    # basic: strip any dots
    needle = re.sub("\.\./", "", needle)
    needle = re.sub("\.", "", needle)
    # cleanup
    needle = re.sub('"', '', needle)
    needle = re.sub('', '', needle)

    # print("needle", needle)
    if (project_files is None):
        return False

    # build search expression
    regex = ".*"
    for i in needle:
        regex += i + ".*"
    regex = re.compile(regex)

    # get matching files
    completions = []
    for file in project_files:
        if (re.match(regex, file)):
            # determine path: relative or abs
            completion = get_completion(current_folder, file)
            # get extension
            path, fileExtension = os.path.splitext(completion)

            if (REQUIRE is True):
                completion = path

            completions.append((file.replace(fileExtension, '') + '\t' + fileExtension[1:], completion))

    # return (completions, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS)
    return (completions, sublime.INHIBIT_WORD_COMPLETIONS)


##
# Returns relative path from base to target
#
# @param {String} base      path
# @param {String} target    path
# @return {String} relative path
def get_completion(base, target):

    global RELATIVE

    if (RELATIVE is False):
        return target

    bases = base.split("/")
    targets = target.split("/")
    result = ""
    index = 0

    # step back base, until in same folder
    size = len(bases)

    # find common folder
    while (index < size and bases[index] == targets[index]):
        index += 1

    # strip common folders
    del bases[0:index]
    del targets[0:index]

    if (len(bases) == 0):
        # from base path?
        result = './'
    else:
        result = "../" * len(bases)

    result += "/".join(targets)
    return result


###
# Returns a list of javascript files within the given folder
#
# @param {String} project_folder    string to subtract from file path
# @param {String} path              to parent folder
# @param {Array} exclude_folders    of search
# @param {Array} containing files
def get_js_files(project_folder, path, exclude_folders):

    files = []
    ressources = os.listdir(path)
    for ressource in ressources:

        current_path = os.path.join(path, ressource)

        if (os.path.isfile(current_path)):

            if (ressource.endswith('.js')):
                files.append(current_path.replace(project_folder, ""))

        elif (not ressource.startswith('.') and os.path.isdir(current_path)):

            if (not ressource in exclude_folders):
                files += get_js_files(project_folder, current_path, exclude_folders)

    return files


###
# Returns true if the current file is invalid for require completions
#
# @param {Array} folders    project folders
# @param {String} file      path to current view
def abort(folders, file):

    if (file is None):
        print("__CompletePath__ [A] file is None")
        return True

    # not a js file?
    if (not file.endswith(".js")):
        # print("[A] ", file, "not a javascript file")
        return True

    # single file?
    if (len(folders) == 0):
        print("__CompletePath__ [A] no folders")
        return True

    # independent file?
    if (not folders[0] in file):
        print("__CompletePath__ [A] independent file")
        return True

    # multiple folders?
    if (len(folders) > 1):
        print ("__CompletePath__ [W] multiple folders not yet supported")

    return False
