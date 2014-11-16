import re

class Scope:
	"""
		Retrieves path from a valid string scope
	"""
	def get_path(view):
		if not Scope.is_string(view):
			return False

		content = Scope.get_content(view)
		if (Scope.valid_path(content[0])):
			return content
		else:
			return False

	def get_current_scope(view):
		# return inner scope at current cursor position
		scopes = view.scope_name(view.sel()[0].a).strip().split(" ")
		return scopes.pop()

	def is_string(view):
		# return boolean if current cursor is within a string
		return "string" in Scope.get_current_scope(view)

	def get_content(view):
		# returns the contents of the current scope
		region = view.extract_scope(view.sel()[0].a)
		scope_content = view.substr(region).strip()
		# string may be: "", strip it
		# if re.search("[\"\'()]", scope_content[0]):
		# 	scope_content = scope_content[1:]
		# if re.search("[\"\'()]", scope_content[-1]):
		# 	scope_content = scope_content[:-1]
		return [scope_content, region]

	def valid_path(string):
		# returns true if the string may be a valid filepath
		result = re.search("^[A-Za-z0-9/-_$.]*$", string)
		# print("validation", string, result, result is not None)
		return result is not None
