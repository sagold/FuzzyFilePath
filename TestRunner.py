"""
	FuzzyFilePath unit and integration test runner

	Usage:
		Bind a shortcut like
		{ "keys": ["super+y"], "command": "ffp_test_runner" }
		to execute tests. Make sure a default view is selected (not console)

"""
import sublime
import sublime_plugin
import traceback

from FuzzyFilePath.test.unit.tests import tests as unitTests
from FuzzyFilePath.test.integration.tests import tests as integrationTests
from FuzzyFilePath.test.integration.tools import ViewHelper

LINE = "----------------"


class FfpTestRunner(sublime_plugin.TextCommand):

	tools = None,

	def console_blur(self):
		window = sublime.active_window()
		window.focus_group(0)
		window.focus_view(window.active_view())

	def console_open(self):
		window = sublime.active_window()
		window.run_command("show_panel", {"panel": "console", "toggle": False})
		self.console_blur()

	def after(self):
		self.tools.move_cursor(0, 0)
		# delete text
		selection = self.tools.view.sel()[0]
		position = selection.begin()
		region = self.tools.view.line(position)
		self.tools.view.erase(self.tools.edit, region)

	def setUp(self, edit):
		self.console_blur()
		window = sublime.active_window()
		self.tools = ViewHelper(window, window.new_file(), edit)

	def closeView(self): {
		self.tools.view.close()
	}

	def tearDown(self, failed_tests, total_tests):
		# self.tools.view.close()
		print(LINE)
		if failed_tests > 0:
			notice = "{0} of {1} tests failed".format(failed_tests, total_tests)
			print(notice)
			sublime.status_message("FFP Intergration: " + notice)
		else:
			notice = "{0} tests successful".format(total_tests)
			print(notice)
			sublime.status_message("FFP Intergration: " + notice)

	def run(self, edit):
		print("\nFuzzyFilePath Integration Tests")
		total_tests = 0
		failed_tests = 0

		# run unit tests
		for testCase in unitTests:
			total_tests += testCase.length
			for should in testCase.tests:
				test = getattr(testCase, should)

				if "before_each" in dir(testCase):
					testCase.before_each()

				try:
					test()
				except:
					failed_tests += 1
					print("\n" + testCase.name + " " + should + ":")
					print(LINE)
					traceback.print_exc()
					print(LINE)
					print()
					pass

				if "after_each" in dir(testCase):
					testCase.after_each()

		# run integration tests
		for testCase in integrationTests:
			self.setUp(edit)
			total_tests += testCase.length

			for should in testCase.tests:
				test = getattr(testCase, should)

				if "before_each" in dir(testCase):
					testCase.before_each(self.tools)

				try:
					test(self.tools)
				except:
					failed_tests += 1
					print("\n" + testCase.name + " " + should + ":")
					print(LINE)
					traceback.print_exc()
					print(LINE)
					print()
					pass

				if "after_each" in dir(testCase):
					testCase.after_each(self.tools)

				if not testCase.unit_test:
					self.after()

				self.closeView()

		self.tearDown(failed_tests, total_tests)

		if failed_tests > 0:
			self.console_open()
