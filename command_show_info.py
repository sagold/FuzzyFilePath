import sublime_plugin

from FuzzyFilePath.project.ProjectManager import ProjectManager
import FuzzyFilePath.project.validate as Validate


class FfpShowInfoCommand(sublime_plugin.TextCommand):
    """ shows a message dialog with project validation status of current file """
    def run(self, edit):
        project = ProjectManager.get_current_project()
        if project:
            Validate.view(self.view, project.get_settings(), True)
