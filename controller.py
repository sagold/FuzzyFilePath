from FuzzyFilePath.common.verbose import verbose

from FuzzyFilePath.project.CurrentFile import CurrentFile
from FuzzyFilePath.project.ProjectManager import ProjectManager
from FuzzyFilePath.FuzzyFilePath import FuzzyFilePath


ID = "Controller"


def get_filepath_completions(view):
	completions = False
	if CurrentFile.is_valid():
	    verbose(ID, "get filepath completions")
	    #completions = FuzzyFilePath.get_filepath_completions(view, CurrentFile.get_project_directory(), CurrentFile.get_directory())
	    completions = FuzzyFilePath.on_query_completions(view, CurrentFile.get_project_directory(), CurrentFile.get_directory())
	return completions


def on_query_completion_inserted(view, post_remove):
	if FuzzyFilePath.completion_active():
	    verbose(ID, "query completion inserted")
	    #FuzzyFilePath.update_inserted_filepath(view, post_remove)
	    FuzzyFilePath.on_post_insert_completion(view, post_remove)
	    FuzzyFilePath.completion_stop()

def on_query_completion_aborted():
	FuzzyFilePath.completion_stop()

def on_project_focus(window):
	"""a new window has received focus"""
	verbose(ID, "focus project")
	ProjectManager.update_project(window)


def on_project_activated(window):
	"""a new project has received focus"""
	verbose(ID, "activate project")
	ProjectManager.activate_project(window)


def on_file_created(view):
	"""a new file has been created"""
	ProjectManager.rebuild_filecache()


def on_file_focus(view):
	CurrentFile.evaluate_current(view, ProjectManager.get_current_project())
