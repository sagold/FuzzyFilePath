import copy
import sublime
import sublime_plugin

from FuzzyFilePath.project.validate import Validate
from FuzzyFilePath.project.project_files import ProjectFiles


ProjectCache = {}


class ProjectManager(sublime_plugin.EventListener):

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

	def add_file(file_name):
		if ProjectManager.current_project:
			ProjectManager.current_project.add_file(file_name)

	def update_project(window):
		if ProjectManager.active:
			return ProjectManager.rebuild_filecache()

	def activate_project(window):
		if ProjectManager.active:
			ProjectManager.current_project = ProjectManager.get_project(window)

	def get_current_project():
		return ProjectManager.current_project

	def has_current_project():
		return ProjectManager.current_project is not False

	def get_project(window):
		project_settings = get_project_settings(window)
		if project_settings is False:
			return False

		project_folder = get_project_folder(window)
		project = ProjectCache.get(project_folder)
		if project is None:
			project = ProjectManager.ProjectConstructor(window, project_folder, project_settings, ProjectManager.ffp_settings)
			ProjectCache[project_folder] = project

		return project

	# delegate

	def cache_directory(directory):
		if ProjectManager.current_project:
			ProjectManager.current_project.cache_directory(directory)

	def rebuild_filecache():
		if ProjectManager.current_project:
			ProjectManager.current_project.rebuild_filecache()
		return

	def update_filecache(folder, filename):
		if ProjectManager.current_project:
			ProjectManager.current_project.update_filecache(folder, filename)
		return

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


def get_project_settings(window):
	"""
		returns project settings. If not already set, creates them
	"""
	data = window.project_data()
	if not data:
		return False
	changed = False
	settings = data.get("settings", False)
	if settings is False:
		changed = True
		settings = {}
		data["settings"] = settings
	ffp = settings.get("FuzzyFilePath")
	if not ffp:
		changed = True
		ffp = {}
		settings["FuzzyFilePath"] = ffp
	if changed:
		window.set_project_data(data)
	return ffp
