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

	def before_each(self, vh):
		global valid_trigger

		Query.reset()
		valid_trigger = {

			"auto": True
		}

	#validation
	def should_abort_on_empty_values(self, vh):
		needle = ""
		current_folder = ""
		project_folder = ""
		trigger = {}

		valid = Query.build(needle, trigger, current_folder, project_folder)

		self.assert_equal(valid, False)

	def should_be_valid_for_auto(self, vh):
		valid = bool(Query.build("", valid_trigger, "", ""))

		self.assert_equal(valid, True)

	#base path
	def should_set_basepath_to_current_folder(self, vh):
		valid_trigger["relative"] = True

		Query.build("", valid_trigger, "current_folder", "")

		self.assert_equal(Query.base_path, "current_folder")

	def should_set_base_directory_for_relative_queries(self, vh):
		valid_trigger["relative"] = True
		valid_trigger["base_directory"] = "base_directory"

		Query.build("", valid_trigger, "current_folder", "")

		self.assert_equal(Query.base_path, "base_directory")

	def should_not_set_basepath_for_absolute_queries(self, vh):
		valid_trigger["relative"] = False

		Query.build("", valid_trigger, "current_folder", "")

		self.assert_equal(Query.base_path, False)

	#basepath override by needle
	def should_prefer_needletype_over_relative_setting_01(self, vh):
		valid_trigger["relative"] = True

		Query.build("/absolute", valid_trigger, "current_folder", "")

		self.assert_equal(Query.base_path, False)

	def should_prefer_needletype_over_relative_setting_02(self, vh):
		valid_trigger["relative"] = False

		Query.build("../relative", valid_trigger, "current_folder", "")

		self.assert_equal(Query.base_path, "current_folder")

	#basepath override by command
	def should_prefer_command_over_rel(self, vh):
		valid_trigger["relative"] = True
		Query.force("filepath_type", "absolute")

		Query.build("../relative", valid_trigger, "current_folder", "")

		self.assert_equal(Query.base_path, False)

	def should_prefer_command_over_abs(self, vh):
		valid_trigger["relative"] = False
		Query.force("filepath_type", "relative")

		Query.build("/absolute", valid_trigger, "current_folder", "")

		self.assert_equal(Query.base_path, "current_folder")

