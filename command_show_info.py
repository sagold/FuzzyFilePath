import sublime_plugin
import FuzzyFilePath.current_state as state
import FuzzyFilePath.project.validate as Validate


class FfpShowInfoCommand(sublime_plugin.TextCommand):
    """ shows a message dialog with project validation status of current file """
    def run(self, edit):
        Validate.view(self.view, state.get_settings(), True)

