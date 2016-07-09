"""
    Manage active state of completion and post cleanup
"""
import re
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.config import config


state = {
    "active": False,        # completion currently in progress (serve suggestions)
    "onInsert": [],         # substitutions for building final path
    "base_directory": False # base directory to set for absolute path, enabled by query...
}

def start(post_replacements=[]):
    state["replaceOnInsert"] = post_replacements
    state["active"] = True

def stop():
    state["active"] = False
    # set by query....
    state["base_directory"] = False

def is_active():
    return state.get("active")

def set_base_directory(directory):
    state["base_directory"] = directory

def get_final_path(path):
    # hack reverse
    path = re.sub(config["ESCAPE_DOLLAR"], "$", path)
    for replace in state.get("replaceOnInsert"):
        path = re.sub(replace[0], replace[1], path)

    if state.get("base_directory") and path.startswith("/"):
        path = re.sub("^\/" + state.get("base_directory"), "", path)
        path = Path.sanitize(path)

    return path
