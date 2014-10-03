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

		assert word == "pathAtCursor", "expected '%s' to be 'pathAtCursor'" % word


	def should_not_return_empty_strings(self, viewHelper):
		viewHelper.set_line('""')
		viewHelper.move_cursor(0, 1)

		word = get_word_at_cursor(viewHelper.view)[0]

		assert word == "", "expected '%s' to be empty" % word


	def should_not_return_whitespaces(self, viewHelper):
		viewHelper.set_line('"    "')
		viewHelper.move_cursor(0, 3)

		word = get_word_at_cursor(viewHelper.view)[0]

		assert word == "", "expected '%s' to be empty" % word


	def should_not_contain_special_characters(self, viewHelper):
		viewHelper.set_line('")')
		viewHelper.move_cursor(0, 0)

		word = get_word_at_cursor(viewHelper.view)[0]

		assert word == "", "expected '%s' to be empty" % word
