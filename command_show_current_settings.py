import json
import sublime
import sublime_plugin
import FuzzyFilePath.common.settings as settings


class FfpShowCurrentSettingsCommand(sublime_plugin.TextCommand):
    """ shows a message dialog with project validation status of current file """
    def run(self, edit):
        json_string = json.dumps(settings.current(), indent=4, sort_keys=True)
        new_file = sublime.active_window().new_file()
        new_file.insert(edit, 0, json_string)
        new_file.set_syntax_file("Packages/JavaScript/JavaScript.tmLanguage")
