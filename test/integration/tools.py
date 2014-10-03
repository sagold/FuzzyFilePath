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

	def set_line(self, string):
		self.view.insert(self.edit, 0, string)

	def move_cursor(self, line, column):
		pt = self.view.text_point(line, column)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(pt))
		self.window.focus_view(self.view)
		# vim
		self.view.run_command('_enter_insert_mode')
