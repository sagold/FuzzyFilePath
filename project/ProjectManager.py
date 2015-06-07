import copy
import sublime
import sublime_plugin

from FuzzyFilePath.common.verbose import verbose
import FuzzyFilePath.project.validate as Validate
from FuzzyFilePath.project.CurrentFile import CurrentFile
import FuzzyFilePath.common.settings as Settings

ProjectCache = {}


ID = "ProjectManager"

class ProjectManager(sublime_plugin.EventListener):
	""" registers projects and keeps track of current project (in conjuction with ProjectListener) """

	active = False
	current_project = False
	ffp_settings = None
	ProjectConstructor = None

	def initialize(ProjectConstructor, ffp_settings):
		ProjectManager.ProjectConstructor = ProjectConstructor
		ProjectManager.ffp_settings = ffp_settings
		ProjectManager.active = True
		ProjectManager.activate_project(sublime.active_window())

	def set_settings(config, extensionsToSuggest):
		ProjectManager.config = config
		ProjectManager.extensions = extensionsToSuggest

	def update_project(window):
		if ProjectManager.active:
			return ProjectManager.rebuild_filecache()

	def activate_project(window):
		if ProjectManager.active:
			# fetch project
			ProjectManager.current_project = ProjectManager.get_project(window)
			CurrentFile.evaluate_current(window.active_view(), ProjectManager.get_current_project())

			if ProjectManager.has_current_project():
				# update project settings
				project_settings = Settings.project(window)
				ProjectManager.get_current_project().update_settings(ProjectManager.ffp_settings, project_settings)
				verbose(ID, "activate project", ProjectManager.get_current_project().get_directory())
		else:
			verbose(ID, "this is not a project")

	def get_current_project():
		return ProjectManager.current_project

	def has_current_project():
		return ProjectManager.current_project is not False

	def get_project(window):
		project_settings = Settings.project(window)
		if project_settings is False:
			return False

		project_folder = get_project_folder(window)
		project = ProjectCache.get(project_folder)
		if project is None:
			project = ProjectManager.ProjectConstructor(window, project_folder, project_settings, ProjectManager.ffp_settings)
			ProjectCache[project_folder] = project

		return project

	# delegate

	def rebuild_filecache():
		if ProjectManager.current_project:
			ProjectManager.current_project.rebuild_filecache()

	def update_filecache(folder, filename):
		self.rebuild_filecache()

	def search_completions(needle, project_folder, valid_extensions, base_path=False):
		if ProjectManager.current_project:
			return ProjectManager.current_project.search_completions(needle, project_folder, valid_extensions, base_path)


def get_project_folder(window):
	"""
		returns project directory

		if multiple independent folders are detected, the first folder is returned and a warning is printed
		-> multiple independent folders are not yet supported, which results in ignored folders
		-> ignored folders are not cached nor proposed
	"""
	folders = window.folders()
	if len(folders) == 1:
		return folders[0]

	project_folder = False
	for folder in folders:
		if project_folder is False:
			project_folder = folder
		elif folder in project_folder:
			# set the lowest folder as project folder
			project_folder = folder
		# elif project_folder in folder:
		# 	# ignore, lowest folder as project folder
		elif project_folder not in folder:
			print("Warning. Multiple independent folders found:")
			print("current project folder", project_folder)
			print("secondary project folder", folder)

	return project_folder
