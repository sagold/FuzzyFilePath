"""
    Manage active state of completion and post cleanup
"""
import re
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.config import config
from FuzzyFilePath.common.string import get_diff
import FuzzyFilePath.expression as Context
from FuzzyFilePath.common.verbose import log

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


def update_inserted_filepath(view, start_expression, post_remove):
    """adjusts inserted filepath - post completion"""
    expression = Context.get_context(view)

    # diff of previous needle and inserted needle
    diff = get_diff(post_remove, expression["needle"])
    # cleanup string
    final_path = re.sub("^" + diff["start"], "", expression["needle"])
    # do not replace current word
    if diff["end"] != start_expression["word"]:
        final_path = re.sub(diff["end"] + "$", "", final_path)

    # remove path query completely
    final_path = get_final_path(final_path)
    log("post cleanup path:'", expression.get("needle"), "' ~~> '", final_path, "'")

    # replace current query with final path
    view.run_command("ffp_replace_region", {
        "a": expression["region"].a,
        "b": expression["region"].b,
        "string": final_path,
        "move_cursor": True
    })
