import sublime_plugin
from FuzzyFilePath.project.ProjectManager import ProjectManager


class FfpUpdateCacheCommand(sublime_plugin.TextCommand):
    """ force update project-files cache """
    def run(self, edit):
        ProjectManager.rebuild_filecache()
