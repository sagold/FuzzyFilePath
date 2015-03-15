import os
import sublime
import re
import sublime_plugin

from FuzzyFilePath.expression import Context
from FuzzyFilePath.project.ProjectManager import ProjectManager
from FuzzyFilePath.common.path import Path
from FuzzyFilePath.common.verbose import log
from FuzzyFilePath.common.selection import Selection

ID = "goto file"

class FfpGotoFileCommand(sublime_plugin.TextCommand):
    """ go to file """
    def run(self, edit):
        current_directory = os.path.dirname(self.view.file_name())

        context = Context.get_context(self.view)
        if context.get("valid") is False:
            return log(ID, "abort, no valid path given:", context.get("needle"))

        path = context.get("needle")
        project = ProjectManager.get_current_project()

        if not (path and project):
            return log(ID, "path or project invalid", path, project)

        is_relative = Path.is_relative(path)
        if is_relative:
            path = Path.get_absolute_path(current_directory, path)
            path = re.sub(project.get_directory(), "", path)

        path = re.sub("^[\\\\/\.]", "", path)
        files = project.find_file(path)

        if len(files) == 0:
            return log(ID, "failed finding file", path)

        if len(files) == 1:
            self.open_file(project.get_directory(), files[0])
        else:
            # if javascript, search for index.js
            current_scope = self.view.scope_name(Selection.get_position(self.view))
            if re.search("\.js ", current_scope):
                for file in files:
                    if "index.js" in file:
                        return self.open_file(project.get_directory(), file)

            self.files = files
            self.project_folder = project.get_directory()
            self.view.show_popup_menu(files, self.select_file)

    def select_file(self, index):
        self.open_file(self.project_folder, self.files[index])
        self.files = None
        self.project_folder = None

    def open_file(self, project_folder, filepath):
        path = os.path.join(project_folder, filepath)
        sublime.active_window().open_file(path)

