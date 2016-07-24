from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.common.config import config
from FuzzyFilePath.project.Project import get_root_folder

class FolderMock:
	def __init__(self, directory):
		self.directory = directory


class Test(TestCase):

	def should_return_outer_most_folder(self):
		folders = [FolderMock("/Users/Spock"), FolderMock("/Users/Spock/Pictures")]
		result = get_root_folder("/Users/Spock/Pictures/Uhura", folders)

		self.assert_equal(result.directory, "/Users/Spock")

	def should_return_valid_folders_only(self):
		folders = [FolderMock("/Lib"), FolderMock("/Users"), FolderMock("/Users/Spock/Lib")]
		result = get_root_folder("/Users/Spock", folders)

		self.assert_equal(result.directory, "/Users")

	def should_return_false_if_no_directory_found(self):
		folders = [FolderMock("/Lib"), FolderMock("/Users/Spock"), FolderMock("/Users/Spock/Lib")]
		result = get_root_folder("/Users/Kirk", folders)

		self.assert_equal(result, False)

