import sublime
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.config import config


map_settings = {
    "TRIGGER": "scopes"
}


def project(window):
    """ returns project settings """
    data = window.project_data()
    if not data:
        return {}
    settings = data.get("settings", {})
    ffp_project_settings = settings.get("FuzzyFilePath", {})
    return ffp_project_settings


def get(window):
    """ Returns all settings (default, user, project) merged by standard rules """
    project_settings = project(window)
    global_settings = update()
    for key in global_settings:
        project_settings[key] = project_settings.get(key.lower(), global_settings[key])
    return project_settings


def get_global_settings():
    """ Returns settings retrieved by merged settings files """
    return config

def update():
    """ merges plugin settings with user settings by default """
    ffp_settings = sublime.load_settings(config["FFP_SETTINGS_FILE"])
    global_settings = merge(config, ffp_settings)

    if global_settings["BASE_DIRECTORY"]:
        global_settings["BASE_DIRECTORY"] = Path.sanitize_base_directory(global_settings["BASE_DIRECTORY"])

    if global_settings["PROJECT_DIRECTORY"]:
        global_settings["PROJECT_DIRECTORY"] = Path.sanitize_base_directory(global_settings["PROJECT_DIRECTORY"])

    return global_settings


def merge(settings, overwrite):
    if not overwrite:
        return settings

    """ update settings by given overwrite """
    for key in settings:
        settings[key] = overwrite.get(key.lower(), settings[key])
    # support old config schema
    for key in map_settings:
        mappedKey = map_settings[key]
        settings[key] = overwrite.get(mappedKey, settings[key])

    return settings
