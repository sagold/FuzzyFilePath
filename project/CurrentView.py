"""
    Evaluates and caches current file`s project status
"""
from FuzzyFilePath.project.View import View
from FuzzyFilePath.common.verbose import verbose
import FuzzyFilePath.common.path as Path


ID = "CurrentFile"


state = {

    "cache": {},
    "current": False,
    "default": View()
}

def invalidate():
    state["current"] = state.get("default")


def load_current_view(view, project_directory):
    cache = state.get("cache").get(view.id())
    if cache:
        verbose(ID, "file cached", cache)
        state["current"] = cache
        return cache

    file_name = Path.posix(view.file_name())
    if not file_name:
        # not saved on disk
        state["current"] = View().set_temp(True)
        state.get("cache")[view.id()] = state.get("current")
        verbose(ID, "file not saved")
        return

    if not project_directory or project_directory not in file_name:
        # not within project
        invalidate()
        verbose(ID, "file not within a project")
        return

    # add current view to cache
    state["current"] = View(project_directory, file_name)

    verbose(ID, "File cached", file_name)
    state.get("cache")[view.id()] = state.get("current")

def invalidate_view(id):
    state.get("cache")[id] = None

def is_valid():
    current = state.get("current")
    return False if not current else current.get_project_directory() is not False


def get_project_directory():
    return state.get("current").get_project_directory()


def get_directory():
    return state.get("current").get_directory()


def is_temp():
    current = state.get("current")
    return False if not current else current.is_temp()
