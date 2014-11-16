from FuzzyFilePath.test.tools import TestCase
from FuzzyFilePath.Scope import Scope


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

		is_string = Scope.is_string(viewHelper.view)

		assert is_string == True, "expected '%s' to be 'True'" % is_string

	def should_return_true_if_scope_string(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require(./path/in/string/scope)')
		viewHelper.move_cursor(0, 12)

		is_string = Scope.is_string(viewHelper.view)

		assert is_string == False, "expected '%s' to be 'False'" % is_string

	def should_return_scope_contents(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/in/string/scope")')
		viewHelper.move_cursor(0, 12)

		content = Scope.get_content(viewHelper.view)[0]

		assert content == "./path/in/string/scope", "expected '%s' to be './path/in/string/scope'" % content

	def should_return_true_for_valid_characters(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/in/string/$scope.js")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_content(viewHelper.view)[0]

		valid = Scope.valid_path(content)

		assert valid == True, "expected '%s' to be 'True'" % valid

	def should_be_false_if_contains_brackets(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path(string/$scope.js")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_content(viewHelper.view)[0]

		valid = Scope.valid_path(content)

		assert valid == False, "expected '%s' to be 'False'" % valid

	def should_be_false_if_contains_quotes(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("./path/i\'n/string/$scope.js")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_content(viewHelper.view)[0]

		valid = Scope.valid_path(content)

		assert valid == False, "expected '%s' to be 'False'" % valid

	def should_be_false_if_contains_linebreak(self, viewHelper):
		viewHelper.set_js_syntax()
		viewHelper.set_line('require("valid/path/contains\nlinebreak")')
		viewHelper.move_cursor(0, 12)
		content = Scope.get_content(viewHelper.view)[0]

		valid = Scope.valid_path(content)

		assert valid == False, "expected '%s' to be 'False'" % valid
		viewHelper.undo(1)

	# def should_be_valid_if_empty(self, viewHelper):
	# 	viewHelper.set_js_syntax()
	# 	viewHelper.set_line('require("")')
	# 	viewHelper.move_cursor(0, 9)
	# 	content = Scope.get_content(viewHelper.view)

	# 	valid = Scope.valid_path(content)

	# 	assert valid == True, "expected '%s' to be 'True'" % valid


