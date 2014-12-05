"""
	get word at cursor
"""
from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.FuzzyFilePath import Query
from FuzzyFilePath.common.config import config

# config["DEBUG"] = True
# config["LOG"] = True

valid_trigger = False

class Test(TestCase):

	unit_test = True

	def should_set_basepath_to_current_folder(self, vh):
		Query.reset()
		query = Query.build("", {
			"relative": True,
			"auto": True
		}, "current_folder", "")

		self.assert_equal(query["base_path"], "current_folder")

	def should_not_set_basepath_for_absolute_queries(self, vh):
		Query.reset()
		query = Query.build("", {
			"relative": False,
			"auto": True
		}, "current_folder", "")

		self.assert_equal(query["base_path"], False)
