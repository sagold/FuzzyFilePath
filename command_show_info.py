import sublime_plugin
import FuzzyFilePath.common.settings as settings
import FuzzyFilePath.project.validate as Validate


class FfpShowInfoCommand(sublime_plugin.TextCommand):
    """ shows a message dialog with project validation status of current file """
    def run(self, edit):
        Validate.view(self.view, settings.current(), True)
