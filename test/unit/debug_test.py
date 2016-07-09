"""
	get word at cursor
"""
from FuzzyFilePath.test.tools import TestCase
import FuzzyFilePath.query as Query
from FuzzyFilePath.common.config import config

# config["DEBUG"] = True
# config["LOG"] = True

valid_trigger = False

class Test(TestCase):

	def should_set_basepath_to_current_folder(self):
		Query.reset()
		Query.build("", {
			"relative": True,
			"auto": True
		}, "current_folder")

		self.assert_equal(Query.get_base_path(), "current_folder")

	def should_not_set_basepath_for_absolute_queries(self):
		Query.reset()
		Query.build("", {
			"relative": False,
			"auto": True
		}, "current_folder")

		self.assert_equal(Query.get_base_path(), False)
