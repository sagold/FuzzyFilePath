"""
	get word at cursor
"""
from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.context import get_word_at_cursor


class Test(TestCase):

	def should_return_character_before_word(self, viewHelper):
		# path = get_path('"./path/in/quotes" another in', "in")
		viewHelper.set_line('"./path/in/quotes" another in')
		viewHelper.move_cursor(0, 10)

		word = get_word_at_cursor(viewHelper.view)[0]

		assert word == "/in", "expected '%s' to be '/in'" % word


	def should_return_word_at_cursor(self, viewHelper):
		viewHelper.set_line('notPartOfPath	/absolute/pathAtCursor	')
		viewHelper.move_cursor(0, 25)

		word = get_word_at_cursor(viewHelper.view)[0]

		assert word == "/pathAtCursor", "expected '%s' to be '/pathAtCursor'" % word


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
