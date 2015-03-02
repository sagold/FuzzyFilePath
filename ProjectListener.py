import sublime
import sublime_plugin

from FuzzyFilePath.project.ProjectManager import ProjectManager


class ProjectListener(sublime_plugin.EventListener):
    """ listens ons window changes, delegating events to project manager """

    previous_view = None
    previous_window = None

    def on_activated(self, view):
        if self.previous_view is not view.id():
            self.previous_view = view.id()
        else:
            self.on_window_activated(view)

        if self.previous_window is not sublime.active_window().id():
            self.previous_window = sublime.active_window().id()
            self.on_window_changed(view)

    # project has been refocused
    def on_window_activated(self, view):
        ProjectManager.update_project(view.window())

    # another (possible) project has been opened/focused
    def on_window_changed(self, view):
        ProjectManager.activate_project(view.window())
