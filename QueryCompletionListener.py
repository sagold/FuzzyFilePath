import re
import sublime_plugin

import FuzzyFilePath.common.selection as Selection
import FuzzyFilePath.expression as Context
from FuzzyFilePath.common.config import config
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.project.CurrentFile import CurrentFile
from FuzzyFilePath.FuzzyFilePath import FuzzyFilePath


ID = "QueryCompletionListener"

class QueryCompletionListener(sublime_plugin.EventListener):

    # tracks on_post_insert_completion
    track_insert = {
        "active": False,
        "start_line": "",
    }
    post_remove = ""

    def on_query_completions(self, view, prefix, locations):
        if config["DISABLE_AUTOCOMPLETION"] and not Query.by_command():
            return False

        if self.track_insert["active"] is False:
            self.start_tracking(view)

        if CurrentFile.is_valid():
            verbose(ID, "-> query completions")
            completions = FuzzyFilePath.on_query_completions(view, CurrentFile.get_project_directory(), CurrentFile.get_directory())
            if completions is not False:
                return completions

        self.finish_tracking(view)
        return False

    def on_post_insert_completion(self, view, command_name):
        if FuzzyFilePath.completion_active():
            verbose(ID, "-> post insert completion")
            FuzzyFilePath.on_post_insert_completion(view, self.post_remove)
            FuzzyFilePath.completion_stop()

    # track post insert insertion
    def start_tracking(self, view, command_name=None):
        self.track_insert["active"] = True
        self.track_insert["start_line"] = Selection.get_line(view)
        """
            - sublime inserts completions by replacing the current word
            - this results in wrong path insertions if the query contains word_separators like slashes
            - thus the path until current word has to be removed after insertion
            - ... and possibly afterwards
        """
        context = Context.get_context(view)
        needle = context.get("needle")
        word = re.escape(Selection.get_word(view))
        self.post_remove = re.sub(word + "$", "", needle)
        verbose(ID, "start tracking", self.post_remove)

    def finish_tracking(self, view, command_name=None):
        self.track_insert["active"] = False
        verbose(ID, "finish tracking")

    def abort_tracking(self):
        self.track_insert["active"] = False
        verbose(ID, "abort tracking")

    def on_text_command(self, view, command_name, args):
        # check if a completion may be inserted
        if command_name in config["TRIGGER_ACTION"] or command_name in config["INSERT_ACTION"]:
            self.start_tracking(view, command_name)
        elif command_name == "hide_auto_complete":
            FuzzyFilePath.completion_stop()
            self.abort_tracking()

    # check if a completion is inserted and trigger on_post_insert_completion
    def on_post_text_command(self, view, command_name, args):
        current_line = Selection.get_line(view)
        command_trigger = command_name in config["TRIGGER_ACTION"] and self.track_insert["start_line"] != current_line
        if command_trigger or command_name in config["INSERT_ACTION"]:
            self.finish_tracking(view, command_name)
            self.on_post_insert_completion(view, command_name)
