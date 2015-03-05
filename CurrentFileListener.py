import re
import copy
import sublime_plugin

from FuzzyFilePath.common.config import config
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.project.validate import Validate
from FuzzyFilePath.project.CurrentFile import CurrentFile
from FuzzyFilePath.project.ProjectManager import ProjectManager

ID = "CurrentFileListener"

class CurrentFileListener(sublime_plugin.EventListener):
    """ Evaluates and caches current file`s project status """

    def on_post_save_async(self, view):
        if CurrentFile.is_temp():
            print(ID, "temp file saved, reevaluate")
            ProjectManager.add_file(view.file_name())
            self.cache[view.id()] = None
            self.on_activated(view)

    def on_activated(self, view):
        # view has gained focus
        CurrentFile.evaluate_current(view, ProjectManager.get_current_project())
