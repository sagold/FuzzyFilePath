import sublime_plugin

import FuzzyFilePath.project.ProjectManager as ProjectManager
import FuzzyFilePath.project.validate as Validate


class FfpShowInfoCommand(sublime_plugin.TextCommand):
    """ shows a message dialog with project validation status of current file """
    def run(self, edit):
        project = ProjectManager.get_current_project()
        if project:
            Validate.view(self.view, project.get_settings(), True)
