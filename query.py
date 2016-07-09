"""
    Build current query based on received modifiers
"""
import re
import FuzzyFilePath.common.path as Path
import FuzzyFilePath.completion as Completion
from FuzzyFilePath.common.verbose import log
from FuzzyFilePath.common.config import config


state = {

    "extensions": ["*"],
    "base_path": False
}

override = {
    # set by insert_path_command: overrideable properties for next query
    "filepath_type": False,
    "extensions": [],
    "base_directory": "",
    "replace_on_insert": []
}


def reset():
    state["extensions"] = ["*"]
    state["base_path"] = False
    state["replace_on_insert"] = []
    override.clear()


def force(key, value):
    override[key] = value


def get(key, default=None):
    return override.get(key, default)


def by_command():
    return bool(override.get("filepath_type", False))


def get_base_path():
    return state.get("base_path")


def get_extensions():
    return state.get("extensions")


def get_needle():
    return state.get("needle")


def get_replacements():
    return state.get("replace_on_insert")


def build(needle, trigger, current_folder):
    """
        updates state object for given trigger. The state object is then used to query the file cache:

        @see completion
        ProjectManager.search_completions(
                query.get_needle(),
                current_file.get_project_directory(),
                query.get_extensions(),
                query.get_base_path()
            )
    """
    triggered = by_command()
    needle = Path.sanitize(needle)
    needle_is_absolute = Path.is_absolute(needle)

    needle_is_path = needle_is_absolute or Path.is_relative(needle)
    if not triggered and trigger.get("auto", False) is False and needle_is_path is False:
        return False

    valid = triggered or (config["AUTO_TRIGGER"] if needle_is_path else trigger.get("auto", config["AUTO_TRIGGER"]))
    if valid is False:
        return False

    """ Set current directory by force, else by trigger:

        TRIGGER
        ----------------------------------------
        False       use current file's directory
        True        use settings: base_directory
        String      use string as base_directory
    """
    base_path = resolve_value("base_directory", trigger, False)
    if base_path is True:
        current_folder = config["BASE_DIRECTORY"]
    elif base_path:
        current_folder = Path.sanitize_base_directory(base_path)

    # notify completion to replace path
    if base_path and needle_is_absolute:
        Completion.set_base_directory(current_folder)

    state["base_path"] = current_folder if resolve_path_type(needle, trigger) == "relative" else False
    state["replace_on_insert"] = resolve_value("replace_on_insert", trigger, [])
    state["extensions"] = resolve_value("extensions", trigger, ["*"])
    state["needle"] = sanitize_needle(needle, current_folder)

    return True


def resolve_path_type(needle, trigger):
    """ ^
        |  Force
        | --------
        |  Needle
        | --------
        | Trigger?
    """
    type_of_path = False
    # test if forced by command
    if override.get("filepath_type"):
        type_of_path = override.get("filepath_type")
    # test path to trigger auto-completion by needle
    elif not by_command() and trigger.get("auto") is False and config["AUTO_TRIGGER"] and Path.is_absolute(needle):
        type_of_path = "absolute"
    elif Path.is_absolute(needle):
        type_of_path = "absolute"
    elif Path.is_relative(needle):
        type_of_path = "relative"
    elif trigger.get("relative") is True:
        type_of_path = "relative"
    elif trigger.get("relative") is False:
        type_of_path = "absolute"

    return type_of_path


def resolve_value(key, trigger, default):
    settings = trigger.get(key, default)
    return override.get(key, settings)


def sanitize_needle(needle, current_folder):
    """
        sanitizes requested path and replaces a starting ./ with the current (local) folder
        returns final needle
    """
    current_folder = "" if not current_folder else current_folder
    needle = re.sub("\.\./", "", needle)
    needle = re.sub("[\\n\\t]", "", needle)

    # remove base path from needle
    if state.get("base_path") and isinstance(current_folder, str) and needle.startswith(current_folder):
        needle = needle[len(state.get("base_path")):]

    needle = needle.strip()

    if needle.startswith("./"):
        needle = current_folder + re.sub("\.\/", "", needle)

    # strip any starting dots or slashes
    needle = re.sub("^[\.\/]*", "", needle)

    return needle
