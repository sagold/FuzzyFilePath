"""
	get word at cursor
"""
from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.FuzzyFilePath import get_path


class Test(TestCase):

	def should_return_abs_path(self, viewHelper):
		path = get_path('/absolute/path/to/file', "path")

		assert path == "/absolute/path/to/file", "expected '%s' to be '/absolute/path/to/file'" % path


	def should_return_relative_path(self, viewHelper):
		path = get_path('../../relative/to/file', "..")

		assert path == "../../relative/to/file", "expected '%s' to be '../../relative/to/file'" % path


	def should_return_word_if_not_found(self, viewHelper):
		path = get_path('../../relative/to/file', "undefined")

		assert path is 'undefined', "expected '%s' to be 'undefined" % path


	def should_be_restricted_to_quotes(self, viewHelper):
		path = get_path('"./path/in/quotes" another in', "in")

		assert path == "./path/in/quotes", "expected '%s' to be './path/in/quotes'" % path