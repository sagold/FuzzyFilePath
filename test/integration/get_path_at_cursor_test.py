"""
	get word at cursor
"""
from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.FuzzyFilePath import get_word_at_cursor


class Test(TestCase):


	def should_return_word_at_cursor(self, viewHelper):
		viewHelper.set_line('notPartOfPath	/absolute/pathAtCursor	')
		viewHelper.move_cursor(0, 25)

		word = get_word_at_cursor(viewHelper.view)[0]

		assert word == "pathAtCursor", "expected %w to be 'pathAtCursor'" % word


	def should_return_empty_string(self, viewHelper):
		word = get_word_at_cursor(viewHelper.view)
		print("emptystring:", word)