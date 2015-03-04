import os
from FuzzyFilePath.project.project_files import ProjectFiles
from FuzzyFilePath.common.verbose import warn
from FuzzyFilePath.common.verbose import verbose

ID = "PROJECT"

class Project():

	filecache = None

	def __init__(self, window, directory, project_settings, ffp_settings):
		"""
			Cache project files and manage project settings

			Parameters
			----
			window : Sublime.Window			- active window associated with project
			project_settings : Dictionary	- project settings (like project.settings.FuzzyFilePath)
			ffp_settings : Dictionary		- config merge with base settings, specified by sublime-settings
		"""
		self.window = window
		self.directory = directory
		self.filecache = ProjectFiles()

		# create final settings object, by merging project specific settings with base settings
		self.settings = {}
		for key in ffp_settings:
			self.settings[key.upper()] = ffp_settings.get(key)

		for key in project_settings:
			self.settings[key.upper()] = project_settings.get(key)


		# pay attention to multiple project folders
		# multiple folders and cached files?
		# - each folder is cached separately, which may result in folders being cached multiple times
		self.init()

	def init(self):
		# validate final project directory (by settings)
		project_directory = os.path.join(self.directory, self.get_setting("PROJECT_DIRECTORY"))
		if os.path.exists(project_directory):
			self.project_directory = project_directory
		else:
			self.project_directory = self.directory
			warn(ID, "project directory in settings in not a valid folder")

		# setup project cache
		triggers = self.settings.get("scopes", self.get_setting("TRIGGER"))
		valid_file_extensions = get_valid_extensions(triggers)
		folders_to_exclude = self.get_setting("EXCLUDE_FOLDERS")
		self.filecache.update_settings(valid_file_extensions, folders_to_exclude)

		print("folder", folders_to_exclude)
		print("extensions", valid_file_extensions)
		print(ID, "Project directory set to", self.project_directory)

		# and start caching
		self.filecache.add(self.project_directory)


	def get_directory(self):
		return self.project_directory

	def get_setting(self, key, default=None):
		return self.settings.get(key, default)

	def get_settings(self):
		return self.settings

	def set_setting(self, key, value):
		data = self.window.get_project_data()
		settings = data.get("settings").get("FuzzyFilePath")
		settings[key] = value
		self.window.set_project_data(data)
		# and update current settings
		self.settings[key] = value

	def cache_directory(self, directory):
		return
		# return self.filecache.add(directory)

	def rebuild_filecache(self):
		return self.filecache.rebuild()

	def update_filecache(self, folder, filename):
		return self.filecache.update(folder, filename)

	def search_completions(self, needle, project_folder, valid_extensions, base_path=False):
		return self.filecache.search_completions(needle, project_folder, valid_extensions, base_path)


def get_valid_extensions(triggers):
	""" return all found extensions in scope triggers """
	extensionsToSuggest = []
	# build extensions to suggest
	for scope in triggers:
	    ext = scope.get("extensions", [])
	    extensionsToSuggest += ext
	# return without duplicates
	return list(set(extensionsToSuggest))
