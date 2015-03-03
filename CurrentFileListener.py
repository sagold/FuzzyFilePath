import sublime_plugin

from FuzzyFilePath.common.config import config
from FuzzyFilePath.project.validate import Validate
from FuzzyFilePath.project.ProjectManager import ProjectManager


class CurrentFile(sublime_plugin.EventListener):
    """ Evaluates and caches current file`s project status """

    cache = {}
    current = {
        "is_temp": False,               # file does not exist in filesystem
        "directory": False,             # directory relative to project
        "project_directory": False      # project directory
    }

    def on_post_save_async(self, view):
        if CurrentFile.is_temp():
            verbose("temp file saved, reevaluate")
            ProjectManager.update_project()

    def on_activated(self, view):
        # view has gained focus
        file_name = view.file_name()
        current = self.cache.get(file_name)

        if current is None or current.get("is_temp"):
            # add current view to cache
            current = CurrentFile.validate(view)
            CurrentFile.cache[file_name] = current

            print("file activated in project directory", current["project_directory"])

            if current["project_directory"]:
                ProjectManager.cache_directory(current["project_directory"])
            # and update project files
            # if project_files and current["project_directory"]:
            #     project_files.add(current["project_directory"])

        CurrentFile.current = current

    def is_valid():
        return CurrentFile.current.get("project_directory") is not False

    def get_project_directory():
        return CurrentFile.current.get("project_directory")

    def get_directory():
        return CurrentFile.current.get("directory")

    def is_temp():
        return CurrentFile.current.get("is_temp")

    def validate(view):
        current = {
            "is_temp": False,
            "directory": False,
            "project_directory": False
        }

        current["is_temp"] = not Validate.file_has_location(view)
        if current["is_temp"]:
            return current

        if not ProjectManager.has_current_project():
            return current

        settings = ProjectManager.get_current_project().get_settings()
        print("current file", settings.get("PROJECT_DIRECTORY"))

        directory = Validate.view(view, settings, False)
        if directory:
            current["project_directory"] = directory["project"]
            current["directory"] = directory["current"]

        return current