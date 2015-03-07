import os
import sublime
import sublime_plugin

from FuzzyFilePath.expression import Context
from FuzzyFilePath.project.ProjectManager import ProjectManager
from FuzzyFilePath.common.path import Path


class FfpGotoFileCommand(sublime_plugin.TextCommand):
    """ go to file """
    def run(self, edit):
    	file_path = self.view.file_name()

    	context = Context.get_context(self.view)
    	if context.get("valid") is False:
    		return

    	path = context.get("needle")
    	project = ProjectManager.get_current_project()
    	is_relative = Path.is_relative(path)
    	if is_relative:
            path = Path.get_absolute_path(file_path, path)
            print("relative path", path)

    	if path and project:
    		files = project.find_file(path)
    		print("goto file", path, files)

    		if len(files) == 0:
    			print("failed finding file", path)
    		elif len(files) == 1:
    			self.open(project.get_directory(), files[0])
    		else:
    			print("multiple files found")


    def open(self, project_folder, filepath):
    	print(project_folder, filepath)
    	path = os.path.join(project_folder, filepath)
    	sublime.active_window().open_file(path)


