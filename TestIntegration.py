"""
	FuzzyFilePath Integration Testrunner

	Usage:
		Bind a shortcut like
		{ "keys": ["super+y"], "command": "ffp_integration" }
		to execute tests. Make sure a default view is selected (not console)

"""
import sublime
import sublime_plugin
import traceback

from FuzzyFilePath.test.integration.tests import tests
from FuzzyFilePath.test.integration.tools import ViewHelper


LINE = "----------------"


class FfpIntegration(sublime_plugin.TextCommand):

	tools = None,

	def after(self):
		self.tools.move_cursor(0, 0)
		# delete text
		selection = self.tools.view.sel()[0]
		position = selection.begin()
		region = self.tools.view.line(position)
		self.tools.view.erase(self.tools.edit, region)


	def setUp(self, edit):
		window = sublime.active_window()
		window.focus_group(1)
		self.tools = ViewHelper(window, window.new_file(), edit)


	def tearDown(self, failed_tests, total_tests):
		self.tools.view.close()
		print(LINE)
		if failed_tests > 0:
			print(failed_tests, "of" , total_tests, "tests failed")
		else:
			print(total_tests, "tests succesful")


	def run(self, edit):
		print("\nFuzzyFilePath Integration Tests")
		total_tests = 0
		failed_tests = 0

		self.setUp(edit)

		for name in tests:
			testCase = tests.get(name)
			total_tests += testCase.length

			for test in testCase.tests:
				try:
					testCase[test](self.tools)
				except:
					failed_tests += 1
					print("\n" + name + " " + test + ":")
					print(LINE)
					traceback.print_exc()
					print(LINE)
					print()
					pass

				self.after()

		self.tearDown(failed_tests, total_tests)
