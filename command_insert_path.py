import sublime_plugin
from FuzzyFilePath.common.config import config
import FuzzyFilePath.query as Query

class InsertPathCommand(sublime_plugin.TextCommand):
    """ trigger customized autocomplete overriding auto settings """
    def run(self, edit, type="default", base_directory=None, replace_on_insert=[], extensions=[]):
        print("INSERT PATH COMMAND")
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        Query.override_trigger_setting("filepath_type", type)
        Query.override_trigger_setting("base_directory", base_directory)

        if len(replace_on_insert) > 0:
            Query.override_trigger_setting("replace_on_insert", replace_on_insert)
        if len(extensions) > 0:
            Query.override_trigger_setting("extensions", extensions)

        self.view.run_command('auto_complete', "insert")