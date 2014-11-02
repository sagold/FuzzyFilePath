from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.context import get_path_at_cursor


class Test(TestCase):

	def should_return_path(self, viewHelper):
		viewHelper.set_line('in "./path/in/quotes" another in')
		viewHelper.move_cursor(0, 12)

		path = get_path_at_cursor(viewHelper.view)[0]

		assert path == "./path/in/quotes", "expected '%s' to be './path/in/quotes'" % path
