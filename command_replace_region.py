import re
import sublime
import sublime_plugin
from FuzzyFilePath.common.config import config

class FfpReplaceRegionCommand(sublime_plugin.TextCommand):

    # helper: replaces range with string
    def run(self, edit, a, b, string, move_cursor=False):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        self.view.replace(edit, sublime.Region(a, b), string)

        if move_cursor and config["POST_INSERT_MOVE_CHARACTERS"]:
        	self.move_skip(a + len(string))

    def move_skip(self, point):
    	length = 0
    	word_region = self.view.word(point)
    	line_region = self.view.line(point)
    	post_region = sublime.Region(word_region.b, line_region.b)
    	post = self.view.substr(post_region)
    	to_move = re.search(config["POST_INSERT_MOVE_CHARACTERS"], post)

    	if to_move:
    		length = len(to_move.group(0))

    	self.move_cursor(point + length)

    def move_cursor(self, point):
    	self.view.sel().clear()
    	self.view.sel().add(sublime.Region(point))
    	self.view.window().focus_view(self.view)
    	self.view.run_command('_enter_insert_mode') # vintageous
