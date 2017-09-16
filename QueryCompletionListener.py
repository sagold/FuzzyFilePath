import re
import sublime_plugin
import FuzzyFilePath.controller as controller
import FuzzyFilePath.common.selection as Selection
import FuzzyFilePath.expression as Context
import FuzzyFilePath.common.settings as settings
from FuzzyFilePath.common.verbose import verbose
import FuzzyFilePath.current_state as state


ID = "QueryCompletionListener"


class QueryCompletionListener(sublime_plugin.EventListener):

    # tracks on_post_insert_completion
    track_insert = {
        "active": False,
        "start_line": "",
    }
    post_remove = ""

    def on_query_completions(self, view, prefix, locations):
        if settings.get("disable_autocompletion") and not Query.by_command():
            return False

        if self.track_insert["active"] is False:
            self.start_tracking(view)

        completions = controller.get_filepath_completions(view)
        if completions is not False:
            return completions

        self.finish_tracking(view)
        return False

    #custom
    def on_post_insert_completion(self, view, command_name):
        controller.on_query_completion_inserted(view, self.post_remove)

    #custom
    def on_query_abort(self):
        controller.on_query_completion_aborted()

    # track post insert insertion
    def start_tracking(self, view, command_name=None):
        if not state.is_valid():
            return

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
        if command_name in settings.get("trigger_action", []) or command_name in settings.get("insert_action", []):
            self.start_tracking(view, command_name)
        elif command_name == "hide_auto_complete":
            self.on_query_abort()
            self.abort_tracking()

    # check if a completion is inserted and trigger on_post_insert_completion
    def on_post_text_command(self, view, command_name, args):
        if len( view.sel() ) < 1:
            return
        current_line = Selection.get_line(view)
        command_trigger = command_name in settings.get("trigger_action", []) and self.track_insert["start_line"] != current_line
        if command_trigger or command_name in settings.get("insert_action", []):
            self.finish_tracking(view, command_name)
            self.on_post_insert_completion(view, command_name)
