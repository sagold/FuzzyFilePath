import sublime
import sublime_plugin

from FuzzyFilePath.project.ProjectManager import ProjectManager
from FuzzyFilePath.project.ProjectManager import get_project_folder


ID = "ProjectListener"

class ProjectListener(sublime_plugin.EventListener):
    """ listens ons window changes, delegating events to project manager """

    previous_project = None
    previous_window = None

    def on_activated(self, view):
        project_folder = get_project_folder(view.window())

        if self.previous_project != project_folder:
            if self.previous_project is not None:
                # print("changed project from", self.previous_project, project_folder)
                self.on_project_activated(view)
            self.previous_project = project_folder

        if self.previous_window is not sublime.active_window().id():
            self.previous_window = sublime.active_window().id()
            self.on_window_activated(view)

    # project has been refocused
    def on_window_activated(self, view):
        print(ID, "window activated -> update current project", view.window().id())
        ProjectManager.update_project(view.window())

    # another (possible) project has been opened/focused
    def on_project_activated(self, view):
        print(ID, "project activated -> activate project", view.window().id())
        ProjectManager.activate_project(view.window())

    # after file has been saved
    # def on_post_save_async(self, view):
    #     if ProjectManager.has_current_project() is False:
    #         return False

    #     # update project by file
    #     folders = sublime.active_window().folders()
    #     match = [folder for folder in folders if folder in view.file_name()]
    #     if len(match) > 0:
    #         return ProjectManager.update_filecache(match[0], view.file_name())
    #     else:
    #         return False
