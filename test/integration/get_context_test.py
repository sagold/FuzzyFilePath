"""
	get word at cursor
"""
from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.expression import get_context


class Test(TestCase):

	def should_return_line_as_needle(self, viewHelper):
		viewHelper.set_line('../line/as/path')
		viewHelper.move_cursor(0, 12)

		needle = get_context(viewHelper.view).get("needle")

		self.assert_equal(needle, '../line/as/path')

	def should_return_word_as_needle(self, viewHelper):
		viewHelper.set_line('result = path')
		viewHelper.move_cursor(0, 12)

		needle = get_context(viewHelper.view).get("needle")

		self.assert_equal(needle, 'path')

	#prefix
	def should_return_prefix_before_bracket(self, viewHelper):
		viewHelper.set_line('prefix(file)')
		viewHelper.move_cursor(0, 8)

		result = get_context(viewHelper.view).get("prefix")

		self.assert_equal(result, 'prefix')

	def should_return_prefix_before_equal(self, viewHelper):
		viewHelper.set_line('prefix=file')
		viewHelper.move_cursor(0, 10)

		result = get_context(viewHelper.view).get("prefix")

		self.assert_equal(result, 'prefix')

	def should_return_prefix_before_colon(self, viewHelper):
		viewHelper.set_line('prefix:file')
		viewHelper.move_cursor(0, 10)

		result = get_context(viewHelper.view).get("prefix")

		self.assert_equal(result, 'prefix')

	#style
	def should_return_style_in_quotes(self, vh):
		vh.set_line('"background": prefix(test)')
		vh.move_cursor(0, 23)

		result = get_context(vh.view).get("style")

		self.assert_equal(result, 'background')

	def should_return_style_in_tag(self, vh):
		vh.set_line('<h1 style=\"\'background\': prefix(\'test\')\"')
		vh.move_cursor(0, 36)

		result = get_context(vh.view)

		self.assert_equal(result.get("tagName"), 'h1')
		self.assert_equal(result.get("style"), 'background')

	#tagName
	def should_retun_tagName(self, vh):
		vh.set_line('<div id')
		vh.move_cursor(0, 10)

		result = get_context(vh.view).get("tagName")

		self.assert_equal(result, 'div')




