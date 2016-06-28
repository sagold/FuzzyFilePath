# Integration Test Helpers
import sublime


class ViewHelper:

	window	= None,
	view	= None,
	edit	= None,

	def __init__(self, window, view, edit):
		self.window = window
		self.view = view
		self.edit = edit

	def undo(self, count=1):
		while count > 0:
			self.view.run_command("undo")
			count -= 1

	def set_js_syntax(self):
		self.view.set_syntax_file("Packages/FuzzyFilePath/test/javascript.tmLanguage")

	def set_line(self, string):
		self.view.insert(self.edit, 0, string)

	def move_cursor(self, line, column):
		pt = self.view.text_point(line, column)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(pt))
		self.window.focus_view(self.view)
		self.view.run_command('_enter_insert_mode', { "mode": "insert" }) # vintageous
