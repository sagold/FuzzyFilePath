import os
import re
import sublime
import sublime_plugin
import FuzzyFilePath.expression as Context
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.verbose import log
import FuzzyFilePath.common.selection as Selection
import FuzzyFilePath.current_state as state


ID = "GotoFile"


class FfpGotoFileCommand(sublime_plugin.TextCommand):
    """ open file under cursor """
    def run(self, edit):
        current_directory = os.path.dirname(self.view.file_name())
        context = Context.get_context(self.view)
        if context.get("valid") is False:
            return log(ID, "abort, no valid path given:", context.get("needle"))

        path = context.get("needle")
        project_folder = state.get_project_directory()

        if not (path and project_folder):
            return log(ID, "path or project invalid", path, project_folder)

        is_relative = Path.is_relative(path)
        if is_relative:
            path = Path.get_absolute_path(current_directory, path)
            path = re.sub(project_folder, "", path)

        path = re.sub("^[\\\\/\.]", "", path)
        files = state.find_file(path)

        if len(files) == 0:
            return log(ID, "failed finding file", path)

        if len(files) == 1:
            self.open_file(project_folder, files[0])
        else:
            # if javascript, search for index.js
            current_scope = self.view.scope_name(Selection.get_position(self.view))
            if re.search("\.js ", current_scope):
                for file in files:
                    if "index.js" in file:
                        return self.open_file(project_folder, file)

            self.files = files
            self.project_folder = project_folder
            self.view.show_popup_menu(files, self.select_file)

    def select_file(self, index):
        self.open_file(self.project_folder, self.files[index])
        self.files = None
        self.project_folder = None

    def open_file(self, project_folder, filepath):
        path = os.path.join(project_folder, filepath)
        sublime.active_window().open_file(path)

