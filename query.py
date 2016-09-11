"""
    Build current query based on received modifiers
"""
import re
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.verbose import log
import FuzzyFilePath.common.settings as settings


state = {

    "extensions": ["*"],
    "base_directory": False,    # path of current query
    "post_remove_path": False   # path to remove on post cleanup
}

# set by insert_path_command: overrideable properties for next query
# "extensions": [],
# "filepath_type": False,
# "base_path": "",
# "replace_on_insert": []
override = {}


def reset():
    state["extensions"] = ["*"]
    state["base_directory"] = False
    state["replace_on_insert"] = []
    override.clear()


def override_trigger_setting(key, value):
    override[key] = value


def by_command():
    return bool(override.get("filepath_type", False))


def get_base_path():
    return state.get("base_directory")


def get_extensions():
    return state.get("extensions")


def get_post_remove_path():
    return state.get("post_remove_path")


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
    needle = Path.sanitize(needle)
    needle_is_absolute = Path.is_absolute(needle)
    needle_is_path = needle_is_absolute or Path.is_relative(needle)

    if not trigger or not (by_command() or (settings.get("auto_trigger") if needle_is_path else trigger.get("auto", settings.get("auto_trigger")))):
        return False

    """ Adjust current folder by specified base folder:

        BASE-FOLDER ->  CURRENT_FOLDER
        ------------------------------------------------------------
        True            use settings base_directory
        String          use string as base_directory
        False           use current file's directory (parameter)
    """
    base_path = resolve_value("base_directory", trigger, False)
    if base_path is True:
        current_folder = settings.get("base_directory")
    elif base_path:
        current_folder = Path.sanitize_base_directory(base_path)

    state["post_remove_path"] = current_folder if (base_path and needle_is_absolute) else False
    state["base_directory"] = current_folder if resolve_path_type(needle, trigger) == "relative" else False
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
    type_of_path = False # OR RELATIVE BY DEFAULT?
    # test if forced by command
    if override.get("filepath_type"):
        type_of_path = override.get("filepath_type")
    # test path to trigger auto-completion by needle
    elif not by_command() and trigger.get("auto") is False and settings.get("auto_trigger") and Path.is_absolute(needle):
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
    if state.get("base_directory") and isinstance(current_folder, str) and needle.startswith(current_folder):
        needle = needle[len(state.get("base_directory")):]

    needle = needle.strip()

    if needle.startswith("./"):
        needle = current_folder + re.sub("\.\/", "", needle)

    # strip any starting dots or slashes
    needle = re.sub("^[\.\/]*", "", needle)

    return needle
