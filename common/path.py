import re

class Path:

	def sanitize(path):
		# sanitize ././
		path = re.sub("^(./)+", "./", path)
		# sanitize slashes (posix)
		path = path.replace("\\", "/")
		return path


	def is_relative(string):
	    return bool(re.match("(\.?\.\/)", string))

	def is_absolute(string):
	    return bool(re.match("\/[A-Za-z0-9\_\-\s\.$]*\/", string))
