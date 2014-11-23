import sublime
import sublime_plugin
from common.config import config

class FfpReplaceRegionCommand(sublime_plugin.TextCommand):

    # helper: replaces range with string
    def run(self, edit, a, b, string):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        region = sublime.Region(int(a), int(b))
        self.view.replace(edit, region, string)
