"""
	manages current state, which include: current filename of view, current project folder if any, project folder
	does not manage settings, but sends a message with the current project folder to settings
"""
ID = "CURRENT STATE"


import sublime
import os
import FuzzyFilePath.common.settings as settings
from FuzzyFilePath.project.FileCache import FileCache
from FuzzyFilePath.project.View import View
import FuzzyFilePath.common.path as Path



def log(*args):
	print("STATE", *args)


valid = False # if the current view is a valid project file
file_caches = {} # caches any file indices of each project folder
state = {} # saves current views state like filename, project_folder, cache and settings

def update():
	""" call me anytime a new view has gained focus. This includes activation of a new window, which should have an
		active view
	"""
	global valid
	temp = False
	window = sublime.active_window()
	if window is None:
		log("Abort -- no active window")
		valid = False
		return valid
	view = window.active_view()
	if view is None:
		log("Abort -- no active view")
		valid = False
		return valid
	file = Path.posix(view.file_name())
	if not file:
		log("Abort -- view has not yet been saved to file")
		temp = True
		return valid
	if state.get("file") == file:
		log("Abort -- view already updated")
		return valid

	folders = list(map(lambda f: Path.posix(f), window.folders()))
	project_folder = get_closest_folder(file, folders)

	if project_folder is False:
		log("Abort -- file not part of a project (folder)")
		valid = False
		return valid

	# notify settings of new project folder
	if state.get("project_folder") != project_folder:
		settings.update_project_settings()
	settings.update_project_folder_settings(project_folder)

	print("\n")
	log("Update")
	valid = True
	# @TODO cache
	# @TODO read settings retrieved from folder settings
	state["file"] = file
	state["folders"] = folders
	state["project_folder"] = project_folder
	state["view"] = View(project_folder, file)
	state["cache"] = get_file_cache(project_folder)
	log("Updated", state)
	return valid


def get_project_directory():
	return state.get("project_folder")


def update_settings():
	if state.get("project_folder"):
		settings.update_project_folder_settings(state.get("project_folder"))


def is_valid():
	return valid


def get_view():
	""" legacy: return the current view """
	return state.get("view")


def get_file_cache(folder):
	if not folder in file_caches:
		valid_file_extensions = get_valid_extensions(settings.get("trigger"))
		log("Build cache for " + folder + " (", valid_file_extensions , ") excluding", settings.get("exclude_folders"))
		file_caches[folder] = FileCache(valid_file_extensions, settings.get("exclude_folders"), folder)

	return file_caches.get(folder)


def rebuild_filecache(folder=None):
	if not folder:
		if state.get("cache"):
			log("rebuild current filecache of folder " + state.get("project_folder"))
			state.get("cache").rebuild()
		return

	folder = Path.posix(folder)
	if not folder in file_caches:
		log("Abort rebuild filecache -- folder " + folder + " not cached")
		return False

	log("rebuild current filecache of folder " + folder)
	file_caches.get(folder).rebuild()


def search_completions(needle, project_folder, valid_extensions, base_path=False):
	return state.get("cache").search_completions(needle, project_folder, valid_extensions, base_path)


def find_file(file_name):
	return state.get("cache").find_file(file_name)


def get_valid_extensions(triggers):
	""" Returns a list of all extensions found in scope triggers """
	extensionsToSuggest = []
	for scope in triggers:
	    ext = scope.get("extensions", [])
	    extensionsToSuggest += ext
	# return without duplicates
	return list(set(extensionsToSuggest))


def get_closest_folder(filepath, directories):
	"""
		Returns the (closest) project folder associated with the given file or False

		# the rational behind this is as follows:
		In nodejs we might work with linked node_modules. Each node_module is a separate project. Adding nested folders
		to the root document thus owns the file and defines the project scope. A separated folder should never reach
		out (via files) on its parents folders.
	"""
	folderpath = os.path.dirname(filepath)
	current_folder = folderpath
	closest_directory = False
	for folder in directories:
		distance = current_folder.replace(folder, "")
		if len(distance) < len(folderpath):
			folderpath = distance
			closest_directory = folder
	return closest_directory
