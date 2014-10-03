from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.FuzzyFilePath import extract_path_from


class Test(TestCase):

	def should_return_abs_path(self, viewHelper):
		path = extract_path_from('/absolute/path/to/file', "path")

		assert path == "/absolute/path/to/file", "expected '%s' to be '/absolute/path/to/file'" % path


	def should_return_relative_path(self, viewHelper):
		path = extract_path_from('../../relative/to/file', "..")

		assert path == "../../relative/to/file", "expected '%s' to be '../../relative/to/file'" % path


	def should_return_word_if_not_found(self, viewHelper):
		path = extract_path_from('../../relative/to/file', "undefined")

		assert path is None, "expected '%s' to be None" % path


	def should_be_restricted_to_quotes(self, viewHelper):
		path = extract_path_from('"./path/in/quotes" another in', "in")

		assert path == "./path/in/quotes", "expected '%s' to be './path/in/quotes'" % path


	# def should_return_match_within_quotes(self, viewHelper):
	# 	path = extract_path_from('another needle "./path/to/needle"', "needle")

	# 	assert path == "./path/to/needle", "expected '%s' to be './path/to/needle'" % path