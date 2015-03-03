from FuzzyFilePath.project.project_files import ProjectFiles


class Project():

	filecache = None

	def __init__(self, window, project_settings, ffp_settings):
		self.window = window
		self.filecache = ProjectFiles()

		self.settings = {}
		for key in ffp_settings:
			self.settings[key.upper()] = project_settings.get(key)

		for key in project_settings:
			print(key, key.upper())
			self.settings[key.upper()] = project_settings.get(key)

		valid_file_extensions = get_valid_extensions(project_settings, ffp_settings)
		folders_to_exclude = project_settings.get("EXCLUDE_FOLDERS", ffp_settings["EXCLUDE_FOLDERS"])
		# setup project cache
		self.filecache.update_settings(valid_file_extensions, folders_to_exclude)

	def get_setting(self, key):
		return self.settings.get(key)

	def set_setting(self, key, value):
		data = self.window.get_project_data()
		settings = data.get("settings").get("FuzzyFilePath")
		settings[key] = value
		self.window.set_project_data(data)

	def get_settings(self):
		return self.settings

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
