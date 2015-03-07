import re
import os
import copy

from FuzzyFilePath.common.config import config
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.project.validate import Validate

ID = "CurrentFile"

class CurrentFile:
    """ Evaluates and caches current file`s project status """

    cache = {}
    current = False
    default = {
        "is_temp": False,               # file does not exist in filesystem
        "directory": False,             # directory relative to project
        "project_directory": False      # project directory
    }

    def evaluate_current(view, project):
        cache = CurrentFile.cache.get(view.id())
        if cache:
            verbose(ID, "file cached", cache)
            CurrentFile.current = cache
            return cache

        if not project:
            # not a project
            verbose(ID, "no project set")
            CurrentFile.current = CurrentFile.default
            return

        file_name = view.file_name()
        if not file_name:
            # not saved on disk
            CurrentFile.current = get_default()
            CurrentFile.current["is_temp"] = True
            CurrentFile.cache[view.id()] = CurrentFile.current
            verbose(ID, "file not saved")
            return

        project_directory = project.get_directory()
        if project_directory not in file_name:
            # not within project
            CurrentFile.current = CurrentFile.default
            verbose(ID, "file not within a project")
            return

        # add current view to cache
        CurrentFile.current = get_default()
        CurrentFile.current["project_directory"] = project_directory
        CurrentFile.current["directory"] = re.sub(project_directory, "", file_name)
        CurrentFile.current["directory"] = re.sub("^[\\\\/\.]*", "", CurrentFile.current["directory"])
        CurrentFile.current["directory"] = os.path.dirname(CurrentFile.current["directory"])

        verbose(ID, "File cached", file_name)
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
