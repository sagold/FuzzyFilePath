import re
import copy
import sublime_plugin

import FuzzyFilePath.controller as controller
import FuzzyFilePath.current_state as state


temp_views = []


def is_valid(view):
    if view.file_name():
        return True
    if not view.id() in temp_views:
        temp_views.append(view.id())
    return False


class ViewListener(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        if view.id() in temp_views:
            self.on_file_created(view)
            self.on_activated(view)

    def on_activated(self, view):
        # view has gained focus
        if is_valid(view):
            controller.on_file_focus(view)

    def on_file_created(self, view):
        temp_views.remove(view.id())
        controller.on_file_created()
