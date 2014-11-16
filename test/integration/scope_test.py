from FuzzyFilePath.test.tools import TestCase
# from FuzzyFilePath.context import get_path_at_cursor

import re

class Scope:

	def get_current_scope(view):
		# return inner scope at current cursor position
		scopes = view.scope_name(view.sel()[0].a).strip().split(" ")
		return scopes.pop()

	def is_string_scope(view):
		# return boolean if current cursor is within a string
		return "string" in Scope.get_current_scope(view)

	def get_scope_content(view):
		# returns the contents of the current scope
		region = view.extract_scope(view.sel()[0].a)
		scope_content = view.substr(region).strip()
		# string may be: "", strip it
		if re.search("[\"\'()]", scope_content[0]):
			scope_content = scope_content[1:]
		if re.search("[\"\'()]", scope_content[-1]):
			scope_content = scope_content[:-1]

		return scope_content

	def valid_path(string):
		# returns true if the string may be a valid filepath
		result = re.search("^[A-Za-z0-9/-_$.]*$", string)
		# print("validation", string, result, result is not None)
		return result is not None


class Test(TestCase):

	def should_return_scope_contents(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/in/string/scope")')
		viewHelper.move_cursor(0, 12)

		scope = Scope.get_current_scope(viewHelper.view)

		assert scope == "string.quoted.js", "expected '%s' to be 'string.quoted.js'" % scope

	def should_return_true_if_scope_string(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/in/string/scope")')
		viewHelper.move_cursor(0, 12)

		is_string = Scope.is_string_scope(viewHelper.view)

		assert is_string == True, "expected '%s' to be 'True'" % is_string

	def should_return_true_if_scope_string(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require(./path/in/string/scope)')
		viewHelper.move_cursor(0, 12)

		is_string = Scope.is_string_scope(viewHelper.view)

		assert is_string == False, "expected '%s' to be 'False'" % is_string

	def should_return_scope_contents(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/in/string/scope")')
		viewHelper.move_cursor(0, 12)

		content = Scope.get_scope_content(viewHelper.view)

		assert content == "./path/in/string/scope", "expected '%s' to be './path/in/string/scope'" % content

	def should_return_true_for_valid_characters(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/in/string/$scope.js")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_scope_content(viewHelper.view)

		valid = Scope.valid_path(content)

		assert valid == True, "expected '%s' to be 'True'" % valid

	def should_be_false_if_contains_brackets(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path(string/$scope.js")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_scope_content(viewHelper.view)

		valid = Scope.valid_path(content)

		assert valid == False, "expected '%s' to be 'False'" % valid

	def should_be_false_if_contains_quotes(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/i\'n/string/$scope.js")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_scope_content(viewHelper.view)
		print("content", content)

		valid = Scope.valid_path(content)

		assert valid == False, "expected '%s' to be 'False'" % valid

	def should_be_false_if_contains_linebreak(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("valid/path/contains\nlinebreak")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_scope_content(viewHelper.view)

		valid = Scope.valid_path(content)

		assert valid == False, "expected '%s' to be 'False'" % valid
		viewHelper.undo(1)

	def should_be_valid_if_empty(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("")')
		viewHelper.move_cursor(0, 9)
		content = Scope.get_scope_content(viewHelper.view)

		valid = Scope.valid_path(content)

		assert valid == True, "expected '%s' to be 'True'" % valid


