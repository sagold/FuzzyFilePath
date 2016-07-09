import re
import copy
import sublime_plugin

import FuzzyFilePath.controller as controller
from FuzzyFilePath.project.CurrentFile import CurrentFile


ID = "CurrentFileListener"

class CurrentFileListener(sublime_plugin.EventListener):
    """ Evaluates and caches current file`s project status """

    def on_post_save_async(self, view):
        if CurrentFile.is_temp():
            CurrentFile.cache[view.id()] = None
            self.on_file_created()
            self.on_activated(view)

    def on_activated(self, view):
        # view has gained focus
        controller.on_file_focus(view)

    def on_file_created(self):
        controller.on_file_created()
