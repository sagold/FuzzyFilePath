from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.context import get_path_at_cursor


class Test(TestCase):

	def should_return_complete_line(self, viewHelper):
		viewHelper.set_line('../path/in/quotes')
		viewHelper.move_cursor(0, 12)

		path = get_path_at_cursor(viewHelper.view)[0]

		assert path == "../path/in/quotes", "expected '%s' to be '../path/in/quotes'" % path

	def should_return_path_in_quotes(self, viewHelper):
		viewHelper.set_line('in "./path/in/quotes" another in')
		viewHelper.move_cursor(0, 12)

		path = get_path_at_cursor(viewHelper.view)[0]

		assert path == "./path/in/quotes", "expected '%s' to be './path/in/quotes'" % path

	def should_return_correct_needle(self, viewHelper):
		viewHelper.set_line('needle /needle needle')
		viewHelper.move_cursor(0, 12)

		path = get_path_at_cursor(viewHelper.view)[0]

		assert path == "/needle", "expected '%s' to be '/needle'" % path

	def should_return_empty_string(self, viewHelper):
		viewHelper.set_line('""')
		viewHelper.move_cursor(0, 1)

		path = get_path_at_cursor(viewHelper.view)[0]

		assert path == "", "expected '%s' to be empty ''" % path
