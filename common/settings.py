"""
    manages the current setting data which is retrieved in the following order (bottom to top)
    - project settings: folder settings
    - project settings
    - user settings file
    - default settings file
    - config
"""
import sublime
import os
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.config import config

# base settings: config, default, user settings file
base_settings = {}
# project settings merged with base settings
project_settings = {}
# final settings object
current_settings = {}
# backwards compatibility of setting schema
map_settings = {
    "trigger": "scopes"
}


def get(key, default=None):
    return current_settings.get(key.lower(), default)


def current():
    return current_settings


def update():
    """ merges plugin settings with user settings by default """
    update_base_settings()
    update_project_settings()


def update_base_settings():
    global base_settings, project_settings, current_settings
    base_settings = get_base_settings(config)
    project_settings = base_settings
    current_settings = base_settings
    #verbose("BASE_SETTINGS", current_settings)


# @TODO improve memory
def update_project_settings():
    global base_settings, project_settings, current_settings
    project_settings = get_project_settings(base_settings)
    current_settings = project_settings
    #verbose("PROJECT_SETTINGS", current_settings)


def update_project_folder_settings(project_folder):
    global project_settings, current_settings
    current_settings = get_folder_settings(project_settings, project_folder)
    #verbose("CURRENT_SETTINGS", current_settings)


def get_project_settings(base):
    """ returns project settings """
    data = sublime.active_window().project_data()
    if not data:
        return base
    ffp_project_settings = data.get("settings", {}).get("FuzzyFilePath", {})
    ffp_project_settings = sanitize(ffp_project_settings)
    return merge(base, ffp_project_settings)


def get_base_settings(config):
    user_settings = sublime.load_settings(config["ffp_settings_file"])
    # Note: user_settings is of class Settings
    user_settings = merge(config, user_settings)
    user_settings = merge_scopes(user_settings)
    return sanitize(user_settings)


def get_folder_settings(project, project_folder=None):
    if not project_folder:
        return project

    folder_settings = get_folder_setting(project_folder)
    folder_settings = sanitize(folder_settings)
    return merge(project, folder_settings)


def merge(settings, overwrite={}):
    """ merge settings object with given overwrite settings """
    result = {}
    for key in settings:
        result[key] = overwrite.get(key.lower(), settings.get(key))
    # backwards compatibility
    for key in map_settings:
        mappedKey = map_settings[key]
        result[key] = overwrite.get(mappedKey, settings.get(key))

    return result


def merge_scopes(settings):
    """Merge triggers from 'additional_scopes' in user settings to the main triggers, if present"""
    triggers = settings.get("trigger")
    additional_scopes = settings.get("additional_scopes", [])
    for trigger in additional_scopes:
        triggers.append(trigger)
    settings["trigger"] = triggers
    return settings


# @TODO improve memory
def get_folder_setting(folder=None):
    """ returns the project config object FuzzyFilePath associated with the given folder """
    if not folder:
        return {}
    data = sublime.active_window().project_data()
    if not data:
        return {}
    folders = data.get("folders")
    if not folders:
        return {}
    # if the project file has been saved, paths in project settings may be relative, but the given filepath is absolute
    # (retrieved from window.folder())
    project_directory = sublime.active_window().project_file_name()
    if project_directory:
        project_directory = os.path.dirname(project_directory)
        folder = Path.relative_to(project_directory, folder)

    for folder_settings in folders:
        if folder_settings.get("path") == folder:
            settings = folder_settings.get("FuzzyFilePath", {})
            verbose("found folder settings", folder, ":", settings)
            return settings

    verbose("no folder settings found", folder)
    return {}


def sanitize(settings_object):
    if "base_directory" in settings_object and settings_object.get("base_directory"):
        settings_object["base_directory"] = Path.sanitize_base_directory(settings_object.get("base_directory"))
    if "project_directory" in settings_object and settings_object.get("project_directory"):
        settings_object["project_directory"] = Path.sanitize_base_directory(settings_object.get("project_directory"))
    return settings_object


def verbose(*args):
    if get("log") is True:
        print("FFP\t", "Settings", *args)
