import json
import sublime
import sublime_plugin

from FuzzyFilePath.project.ProjectManager import ProjectManager


class FfpShowCurrentSettingsCommand(sublime_plugin.TextCommand):
    """ shows a message dialog with project validation status of current file """
    def run(self, edit):
        project = ProjectManager.get_current_project()
        if project:
            settings = project.get_settings()
            json_string = json.dumps(settings, indent=4, sort_keys=True)

            new_file = sublime.active_window().new_file()
            new_file.insert(edit, 0, json_string)
            new_file.set_syntax_file("Packages/JavaScript/Json.tmLanguage")
