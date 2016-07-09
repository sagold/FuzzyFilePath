"""
	get word at cursor
"""
from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.query import Query
from FuzzyFilePath.common.config import config

# config["DEBUG"] = True
# config["LOG"] = True

valid_trigger = False

class Test(TestCase):

	def before_each(self):
		global valid_trigger

		Query.reset()
		valid_trigger = {
			"auto": True
		}

	#validation
	def should_abort_on_empty_values(self):
		needle = ""
		current_folder = ""
		trigger = {}

		valid = Query.build(needle, trigger, current_folder)

		self.assert_equal(valid, False)

	def should_be_valid_for_auto(self):
		valid = bool(Query.build("", valid_trigger, ""))

		self.assert_equal(valid, True)

	#base path
	def should_set_basepath_to_current_folder(self):
		valid_trigger["relative"] = True

		Query.build("", valid_trigger, "current_folder")

		self.assert_equal(Query.get_base_path(), "current_folder")

	def should_set_base_directory_for_relative_queries(self):
		valid_trigger["relative"] = True
		# !Potential problem: path requires a trailing slash (os.path.dirname)
		valid_trigger["base_directory"] = "base_directory/"

		Query.build("", valid_trigger, "current_folder")

		self.assert_equal(Query.get_base_path(), "base_directory")

	def should_not_set_basepath_for_absolute_queries(self):
		valid_trigger["relative"] = False

		Query.build("", valid_trigger, "current_folder")

		self.assert_equal(Query.get_base_path(), False)

	#basepath override by needle
	def should_prefer_needletype_over_relative_setting_01(self):
		valid_trigger["relative"] = True

		Query.build("/absolute", valid_trigger, "current_folder")

		self.assert_equal(Query.get_base_path(), False)

	def should_prefer_needletype_over_relative_setting_02(self):
		valid_trigger["relative"] = False

		Query.build("../relative", valid_trigger, "current_folder")

		self.assert_equal(Query.get_base_path(), "current_folder")

	#basepath override by command
	def should_prefer_command_over_rel(self):
		valid_trigger["relative"] = True
		Query.force("filepath_type", "absolute")

		Query.build("../relative", valid_trigger, "current_folder")

		self.assert_equal(Query.get_base_path(), False)

	def should_prefer_command_over_abs(self):
		valid_trigger["relative"] = False
		Query.force("filepath_type", "relative")

		Query.build("/absolute", valid_trigger, "current_folder")

		self.assert_equal(Query.get_base_path(), "current_folder")

	#swap rel <-> abs
	def should_transform_rel_to_abs_query(self):
		Query.force("filepath_type", "absolute") # set query to be absolute
		Query.build("../folder/sub", valid_trigger, "current_folder") # but insert relative path

		self.assert_equal(Query.get_needle(), "folder/sub")
		self.assert_equal(Query.get_base_path(), False)

	def should_transform_abs_to_rel_query(self):
		Query.force("filepath_type", "relative") # set query to be relative
		Query.build("/folder/sub", valid_trigger, "current_folder") # but insert absolute path

		self.assert_equal(Query.get_needle(), "folder/sub")
		self.assert_equal(Query.get_base_path(), "current_folder")


