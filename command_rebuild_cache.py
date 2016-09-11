import sublime
import sublime_plugin
import FuzzyFilePath.current_state as state


class FfpUpdateCacheCommand(sublime_plugin.TextCommand):
    """ force update project-files cache """
    def run(self, edit):
    	for folder in sublime.active_window().folders():
        	state.rebuild_filecache(folder)
