import sublime_plugin
import FuzzyFilePath.project.ProjectManager as ProjectManager


class FfpUpdateCacheCommand(sublime_plugin.TextCommand):
    """ force update project-files cache """
    def run(self, edit):
        ProjectManager.rebuild_filecache()
