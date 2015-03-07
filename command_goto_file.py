import os
import sublime
import re
import sublime_plugin

from FuzzyFilePath.expression import Context
from FuzzyFilePath.project.ProjectManager import ProjectManager
from FuzzyFilePath.common.path import Path


class FfpGotoFileCommand(sublime_plugin.TextCommand):
    """ go to file """
    def run(self, edit):
        current_directory = os.path.dirname(self.view.file_name())

        context = Context.get_context(self.view)
        if context.get("valid") is False:
            return print("abort, no valid path given")

        path = context.get("needle")
        project = ProjectManager.get_current_project()
        is_relative = Path.is_relative(path)
        if is_relative:
            path = Path.get_absolute_path(current_directory, path)
            path = re.sub(project.get_directory(), "", path)

        path = re.sub("^[\\\\/\.]", "", path)

        if path and project:
            files = project.find_file(path)

            if len(files) == 0:
                print("failed finding file", path)
            elif len(files) == 1:
                self.open_file(project.get_directory(), files[0])
            else:
                self.files = files
                self.view.show_popup_menu(files, self.select_file)

    def select_file(self, index):
        sublime.active_window().open_file(self.files[index])

    def open_file(self, project_folder, filepath):
        path = os.path.join(project_folder, filepath)
        sublime.active_window().open_file(path)

