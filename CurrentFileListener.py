import re
import copy
import sublime_plugin

from FuzzyFilePath.common.config import config
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.project.validate import Validate
from FuzzyFilePath.project.ProjectManager import ProjectManager

ID = "CurrentFile"

class CurrentFile(sublime_plugin.EventListener):
    """ Evaluates and caches current file`s project status """

    cache = {}
    current = False
    default = {
        "is_temp": False,               # file does not exist in filesystem
        "directory": False,             # directory relative to project
        "project_directory": False      # project directory
    }

    def on_post_save_async(self, view):
        if CurrentFile.is_temp():
            print(ID, "temp file saved, reevaluate")
            ProjectManager.add_file(view.file_name())
            self.cache[view.id()] = None
            self.on_activated(view)

    def on_activated(self, view):
        # view has gained focus

        cache = self.cache.get(view.id())
        if cache:
            print(ID, "file cached", cache)
            CurrentFile.current = cache
            return cache

        project = ProjectManager.get_current_project()
        if not project:
            # not a project
            print(ID, "no project set")
            CurrentFile.current = CurrentFile.default
            return

        file_name = view.file_name()
        if not file_name:
            # not saved on disk
            CurrentFile.current = get_default()
            CurrentFile.current["is_temp"] = True
            CurrentFile.cache[view.id()] = CurrentFile.current
            print(ID, "file not saved")
            return

        project_directory = project.get_directory()
        if project_directory not in file_name:
            # not within project
            CurrentFile.current = CurrentFile.default
            print(ID, "file not within a project")
            return

        # add current view to cache
        CurrentFile.current = get_default()
        CurrentFile.current["project_directory"] = project_directory
        CurrentFile.current["directory"] = re.sub(project_directory, "", file_name)
        print(ID, "File cached", file_name)
        CurrentFile.cache[view.id()] = CurrentFile.current


    def is_valid():
        return CurrentFile.current.get("project_directory") is not False

    def get_project_directory():
        return CurrentFile.current.get("project_directory")

    def get_directory():
        return CurrentFile.current.get("directory")

    def is_temp():
        return CurrentFile.current.get("is_temp")

def get_default():
    return copy.copy(CurrentFile.default)
