import sublime_plugin

import FuzzyFilePath.expression as Context
import FuzzyFilePath.common.selection as Selection
from FuzzyFilePath.completion import resolve_trigger
import FuzzyFilePath.current_state as state
import FuzzyFilePath.query as Query


class FfpShowContextCommand(sublime_plugin.TextCommand):
	""" displays the current context, required for debugging and trigger setup """

	content = None

	def run(self, edit):
		context = Context.get_context(self.view)
		current_scope = self.view.scope_name(Selection.get_position(self.view))
		trigger = resolve_trigger(self.view, Query, state.get_view())
		print("FOUND TRIGGER", trigger)

		self.content = "<h4>FuzzyFilepath - context evaluation</h4>"
		self.add("filepath valid", context.get("valid_needle"))
		self.add("context valid", context.get("is_valid"))
		self.content += "<br>"
		self.add("path", context.get("needle"))
		self.add("prefix", context.get("prefix"))
		self.add("property", context.get("style"))
		self.add("tag", context.get("tagName"))
		self.add("word", context.get("word"))
		self.content += "<br>"
		self.add("scope", current_scope)
		self.content += "<br>"
		self.content += "<h5>Trigger</h5>"
		if trigger is False:
			self.content += "no trigger could be found matching the given context"
		else:
			for key in trigger:
				self.add(key, trigger.get(key))

		self.show()

	def add(self, label, value):
		value = "-" if value is None else value
		self.content += "<div><b>" + label + ": </b>" + str(value) + "</div>"

	def show(self):
		self.view.show_popup(self.content)
