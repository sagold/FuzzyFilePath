import FuzzyFilePath.common.path as Path
import FuzzyFilePath.common.settings as Settings
from FuzzyFilePath.common.verbose import warn
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.project.ProjectFolder import ProjectFolder

ID = "PROJECT"


class Project():

	def __init__(self, id, window, ffp_settings):
		self.id = id
		self.directories = []
		project_settings = Settings.project(window)

		for directory in get_independent_directories(window.folders()):
			# TODO add project folder settings...
			# TODO create a folder for each directory but share root's filecache
			self.directories.append(ProjectFolder(window, directory, project_settings, ffp_settings))

	def get_directories(self):
		""" returns a list of directories as strings associated with project. currently used for debugging """
		return list(map(lambda x: x.get_directory(), self.directories))

	def rebuild_filecache(self):
		for directory in self.directories:
			directory.rebuild_filecache()

	def search_completions(self, needle, project_folder, valid_extensions, base_path=False):
		directory = get_closest_folder(project_folder, self.directories)
		if not directory:
			return False

		return directory.search_completions(needle, project_folder, valid_extensions, base_path)

	def get_folder(self, file_name):
		return get_closest_folder(file_name, self.directories)

	def update_settings(self, global_settings, project_settings):
		# TODO: remove & add project folders on changes
		for directory in self.directories:
			directory.update_settings(global_settings, project_settings)


# for list of folders

def get_independent_directories(folders):
	""" Filters paths that are contained in another (lower) path """
	result = [path for path in folders if not has_parent_directory(path, folders)]
	return result


def has_parent_directory(folder, folders):
	""" Returns true if the given path is contained in a path within the list of folders """
	return bool(get_parent_directory(folder, folders))


def get_parent_directory(folder, folders):
	""" Returns the lowest directory which contains the given folder path or False """
	parents = [path for path in folders if path in folder and path is not folder]
	return False if not parents else min(parents, key=len)


def get_root_folder(path, directories):
	current_path = ""
	root = False
	for folder in directories:
		if folder.directory in path:
			distance = path.replace(folder.directory, "")
			if len(distance) > len(current_path):
				current_path = distance
				root = folder

	return root


# for instances of project folders

def get_closest_folder(path, directories):
	current_path = path
	closest_directory = False
	for folder in directories:
		distance = path.replace(folder.directory, "")
		if len(distance) < len(current_path):
			current_path = distance
			closest_directory = folder

	return closest_directory
