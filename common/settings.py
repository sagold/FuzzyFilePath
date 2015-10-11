import sublime
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.config import config


map_settings = {
    "TRIGGER": "scopes"
}


def project(window):
	""" returns project settings. If not already set, creates them """
	data = window.project_data()
	if not data:
		return False

	changed = False
	settings = data.get("settings", False)
	if settings is False:
		changed = True
		settings = {}
		data["settings"] = settings

	ffp_project_settings = settings.get("FuzzyFilePath")
	if not ffp_project_settings:
		changed = True
		ffp_project_settings = {}
		settings["FuzzyFilePath"] = ffp_project_settings
	if changed:
		window.set_project_data(data)

	return ffp_project_settings



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
    """ update settings by given overwrite """
    for key in settings:
        settings[key] = overwrite.get(key.lower(), settings[key])
    # support old config schema
    for key in map_settings:
        mappedKey = map_settings[key]
        settings[key] = overwrite.get(mappedKey, settings[key])

    return settings
