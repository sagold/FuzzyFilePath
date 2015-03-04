from FuzzyFilePath.project.project_files import ProjectFiles


class Project():

	filecache = None

	def __init__(self, window, project_settings, ffp_settings):
		"""
			Cache project files and manage project settings

			Parameters
			----
			window : Sublime.Window			- active window associated with project
			project_settings : Dictionary	- project settings (like project.settings.FuzzyFilePath)
			ffp_settings : Dictionary		- config merge with base settings, specified by sublime-settings
		"""
		self.window = window
		self.filecache = ProjectFiles()

		# create final settings object, by merging project specific settings with base settings
		self.settings = {}
		for key in ffp_settings:
			self.settings[key.upper()] = ffp_settings.get(key)

		for key in project_settings:
			self.settings[key.upper()] = project_settings.get(key)

		# setup project cache
		valid_file_extensions = get_valid_extensions(project_settings, ffp_settings)
		folders_to_exclude = project_settings.get("EXCLUDE_FOLDERS", ffp_settings["EXCLUDE_FOLDERS"])
		self.filecache.update_settings(valid_file_extensions, folders_to_exclude)

		# pay attention to multiple project folders
		# multiple folders and cached files?
		# - each folder is cached separately, which may result in folders being cached multiple times
		print("project created", window.folders())

	def get_setting(self, key):
		return self.settings.get(key)

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
		return self.filecache.add(directory)

	def rebuild_filecache(self):
		return self.filecache.rebuild()

	def update_filecache(self, folder, filename):
		return self.filecache.update(folder, filename)

	def search_completions(self, needle, project_folder, valid_extensions, base_path=False):
		return self.filecache.search_completions(needle, project_folder, valid_extensions, base_path)


def get_valid_extensions(project_settings, ffp_settings):
	extensionsToSuggest = []
	# build extensions to suggest
	triggers = project_settings.get("scopes", ffp_settings["TRIGGER"])
	for scope in triggers:
	    ext = scope.get("extensions", [])
	    extensionsToSuggest += ext
	# return without duplicates
	return list(set(extensionsToSuggest))
