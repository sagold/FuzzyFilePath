import sublime
import sublime_plugin
from common.config import config

class FfpReplaceRegionCommand(sublime_plugin.TextCommand):

    # helper: replaces range with string
    def run(self, edit, a, b, string):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        self.view.replace(edit, sublime.Region(a, b), string)
        # print(self.view.command_history(0))
