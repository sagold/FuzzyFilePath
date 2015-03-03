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

		project = ProjectCache.get(window.id())
		if project is None:
			project = ProjectManager.ProjectConstructor(window, project_settings, ProjectManager.ffp_settings)
			ProjectCache[window.id()] = project

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


def get_project_settings(window):
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
