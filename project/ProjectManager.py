"""
    Manages active projects, activation and deactivation
"""
import sublime
import os


from FuzzyFilePath.common.verbose import verbose
import FuzzyFilePath.project.validate as Validate
import FuzzyFilePath.project.CurrentView as CurrentView
import FuzzyFilePath.common.settings as Settings
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.project.Project import Project

ProjectCache = {}


ID = "ProjectManager"


state = {

    "current_project": False,
    "current_folder": False,
    "ffp_settings": {},
    "ProjectConstructor": None
}

def set_main_settings(ffp_settings):
    state["ffp_settings"] = ffp_settings
    activate_project(sublime.active_window())

def set_settings(config, extensionsToSuggest):
    state["config"] = config
    state["extensions"] = extensionsToSuggest

def update_current_project_folder(view):
    if state["current_project"] is not False and view.file_name():
        state["current_folder"] = state.get("current_project").get_folder(view.file_name())

def activate_project(window):
    """ Retrieves the current project, either from cache or creates a new project

        Note:
            a project is always associated with the a window, but a project may be opened multiple times.
            Furthermore: files may be added that are not within the project project-folders
    """
    view = window.active_view()
    if not view:
        return

    # fetch project
    state["current_project"] = get_project(window)

    if has_current_project():
        CurrentView.load_current_view(view, get_current_project().get_directory())
        # update project settings
        project_settings = Settings.project(window)
        get_current_project().update_settings(state.get("ffp_settings"), project_settings)
        verbose(ID, "activate project", get_current_project())
    else:
        CurrentView.invalidate()

def get_current_project():
    return state.get("current_folder")

def has_current_project():
    return get_current_project() is not False

def get_project(window):
    if not window.folders():
        return False

    # TODO: Add option: Index folder files of non-projects

    # retrieve id of current project. Could also be: window id for non projects else project file
    project_id = window.id()
    project_name = window.project_file_name()
    project = ProjectCache.get(project_name)

    if project is None and ProjectCache.get(project_id):
        project = ProjectCache.get(project_id)

        # if project was saved with its id, but a project name may now be retrieved, rename project to name
        if project_name:
            del ProjectCache[project_id]
            ProjectCache[project_name] = project
        else:
            project_name = project_id

    if project is None:
        project = Project(project_id, window, state["ffp_settings"])
        ProjectCache[project_id] = project

    return project


# delegate

def rebuild_filecache():
    current_folder = get_current_project()
    if current_folder:
        current_folder.rebuild_filecache()

def search_completions(needle, project_folder, valid_extensions, base_path=False):
    current_project = state.get("current_project")
    if current_project:
        return current_project.search_completions(needle, project_folder, valid_extensions, base_path)

def get_project_id(window):
    project_name = window.project_file_name()
    if project_name:
        return project_name
    return window.id()
