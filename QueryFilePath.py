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

# @type {dict} query parameters and cache
Query = {

    "valid": False,
    "current_folder": None,
    "project_folder": None,
    "active": False,
    "relative": False,
    "extension": True,
    "extensions": [],
    "base_path": ""
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

##
# validate request
#
# @param {String} current_scope
# @param {None|Boolean} relativePath or default
def build_query(current_scope, relative=None):

    for properties in Scopes:

        scope = properties.get("scope").replace("//", "")
        if re.search(scope, current_scope):

            Query["auto"] = properties.get("auto", False)
            Query["extension"] = properties.get("insertExtension", True)
            Query["extensions"] = properties.get("extensions", ["js"])
            # Query["base_path"] = properties.get("basePath", False)

            if (relative is None):
                if properties.get("relative") is True:
                    Query["relative"] = Query["current_folder"]
                else:
                    Query["relative"] = False

            return Query

    return False

##
# trigger autocomplete popup
#
# @extends sublime_plugin.TextCommand
class InsertPathCommand(sublime_plugin.TextCommand):

    def run(self, edit, relative=None):

        global Query

        Query["active"] = True
        Query["relative"] = None
        Query["extension"] = True

        if relative is True:
            Query["relative"] = Query["current_folder"]
        elif relative is False:
            Query["relative"] = False

        view = sublime.active_window().active_view()
        selections = view.sel()

        for selection in selections:

            pos = selection.begin()

            if (not "string" in view.scope_name(pos)):
                view.insert(edit, pos, '""')
                pos += 1
                view.sel().clear()
                view.sel().add(sublime.Region(pos))
                view.show(pos)

            else:
                region = view.extract_scope(pos)
                text = view.substr(region)
                text = re.sub("[./]", "", text)
                view.replace(edit, region, text)

        # view.run_command("hide_auto_complete")
        view.run_command('auto_complete')

##
# query autocomplete request
#
# @extends sublime_plugin.EventListener
class QueryFilePath(sublime_plugin.EventListener):

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
            # print("aborting")
            return False

        current_scope = view.scope_name(locations[0])

        if (Query["active"] is True):
            query = build_query(current_scope, Query["relative"])
        else:
            query = build_query(current_scope)

        # evaluate
        if (query is False or (query["active"] is False and query["auto"] is False)):
            return

        # reset
        Query["active"] = False

        view.run_command('_enter_insert_mode')
        scope_region = view.extract_scope(locations[0])
        # might be file contents on wrong scopes
        needle = view.substr(scope_region)

        return project_files.search_completions(needle, query["project_folder"], query["extensions"], query["relative"], query["extension"])

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
