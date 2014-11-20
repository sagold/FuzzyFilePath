import re
import sublime

NEEDLE_SEPARATOR = "\"\'\(\)"
NEEDLE_SEPARATOR_BEFORE = "\"\'\("
NEEDLE_SEPARATOR_AFTER = "^\"\'\)"
NEEDLE_CHARACTERS = "A-Za-z0-9\-\_$"
NEEDLE_INVALID_CHARACTERS = "\"\'\)=\:\(<>"
DELIMITER = "\s\:\(\[\="

# style, tag, prefix, separator
rules = [
    {
        # html
        "scope": "meta.tag.*string.*\\.html",
        # <* src
        "tagName": ["img", "script"],
        "prefix": ["src"],

        "extensions": ["png", "gif", "jpeg", "jpg", "svg"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    },
    {
        # html
        "scope": "meta\\.tag.*string.*\\.html",
        # "scope": "html",
        # <link href
        "tagName": ["link"],
        "prefix": ["href"],

        "extensions": ["css"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    },
    {
        # css
        "scope": "meta\\.property\\-value\\.css",
        # *: url
        "prefix": ["url"],
        "style": ["background-image", "background", "list-type", "list-type-image"],

        "extensions": ["png", "gif", "jpeg", "jpg"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    },
    {
        # css
        "scope": "meta\\.property\\-value\\.css",
        # src: url
        "prefix": ["url"],
        "style": ["src"],

        "extensions": ["woff", "ttf", "svg"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    },
    {
        # js
        "scope": "source\\.js",
        # import * from *
        "prefix": ["from", "import"],

        "extensions": ["js"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    },
    {
        # js
        "scope": "source\\.js.*string",
        # AMD
        "prefix": "define",

        "extensions": ["js"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    },
    {
        # js
        "scope": "source\\.js.*string",
        # js webpack require: require(*)
        "prefix": ["require"],

        "extensions": ["js", "html", "sass", "css", "less", "png", "gif", "jpg", "jpeg"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    },
    {
        # js
        "scope": "source\\.js.*string",
        # object.src = *
        "prefix": ["src"],

        "extensions": ["js", "html", "sass", "css", "less", "png", "gif", "jpg", "jpeg"],
        "auto": True,
        "insertExtension": True,
        "relative": True
    }
]

statements = ["prefix", "tagName", "style"]


def get_context(view):
	selection = view.sel()[0]
	position = selection.begin()
	valid = True

	# regions
	word_region = view.word(position)
	line_region = view.line(position)
	pre_region = sublime.Region(line_region.a, word_region.a)
	post_region = sublime.Region(word_region.b, line_region.b)

	# text
	line = view.substr(line_region)
	word = view.substr(word_region)
	pre = view.substr(pre_region)
	post = view.substr(post_region)
	# print(pre + "|" + word + "|" + post)

	needle_region = view.word(position)

	# print("\n")

	# grab everything in 'separators'
	needle = ""
	separator = False
	pre_match = ""
	pre_quotes = re.search("(["+NEEDLE_SEPARATOR_BEFORE+"])([^"+NEEDLE_SEPARATOR+"]*)$", pre)
	if pre_quotes:
		# # print("pre_quotes: '" + pre_quotes.group(2))
		needle += pre_quotes.group(2) + word
		separator = pre_quotes.group(1)
		pre_match = pre_quotes.group(2)

		needle_region.a -= len(pre_quotes.group(2))

	else:
		pre_quotes = re.search("(\s)([^"+NEEDLE_SEPARATOR+"\s]*)$", pre)
		if pre_quotes:
			needle = pre_quotes.group(2) + word
			separator = pre_quotes.group(1)
			pre_match = pre_quotes.group(2)

			needle_region.a -= len(pre_quotes.group(2))

	if pre_quotes:
		post_quotes = re.search("^(["+NEEDLE_SEPARATOR_AFTER+"]*)", post)
		if post_quotes:
			# # print("post_quotes: '" + post_quotes.group(1))
			needle += post_quotes.group(1)

			needle_region.b += len(post_quotes.group(1))

		else:
			# print("no post quotes found => invalid")
			valid = False
	else:
		needle = word

	# print("needle:'" + needle + "'")
	# print("separator:", separator)

	# grab prefix
	prefix_region = sublime.Region(line_region.a, pre_region.b - len(pre_match) - 1)
	prefix_line = view.substr(prefix_region)
	# # print("prefix line", prefix_line)


	#define? (["...", "..."]) -> before?
	# before: ABC =:([
	prefix = re.search("\s*(["+NEEDLE_CHARACTERS+"]+)["+DELIMITER+"]*$", prefix_line)
	if prefix is None:
		# validate array, like define(["...", ".CURSOR."])
		prefix = re.search("^\s*(["+NEEDLE_CHARACTERS+"]+)["+DELIMITER+"]+", prefix_line)

	if prefix:
		# print("prefix:", prefix.group(1))
		prefix = prefix.group(1)

	tag = re.search("<\s*(["+NEEDLE_CHARACTERS+"]*)\s*[^>]*$", prefix_line)
	if tag:
		tag = tag.group(1)
		# print("tag:", tag)

	style = re.search("\s*(["+NEEDLE_CHARACTERS+"]*)\s*\:[^\:]*$", prefix_line)
	if style:
		style = style.group(1)
		# print("style:", style)

	if separator is False:
		# print("separator undefined => invalid")
		valid = False
	elif re.search("["+NEEDLE_INVALID_CHARACTERS+"]", needle):
		# print("invalid characters in needle => invalid")
		valid = False
	elif prefix is None and separator.strip() == "":
		# print("prefix undefined => invalid")
		valid = False

	if valid is False:
		return False
	else:
		return {
			"needle": needle,
			"prefix": prefix,
			"tagName": tag,
			"style": style,
			"region": needle_region
		}



class Context:

	def get_context(view):
		return get_context(view)

	def check_trigger(trigger, expression):
		# returns True if the expression statements match the trigger
		for statement in set(statements).intersection(trigger):
			values = trigger.get(statement)
			# statement values may be None (or any other value...)
			if type(values) is list and not expression.get(statement) in values:
				return False
			# validate other value by comparison
			# elif not values == expression.get(statement):
			# 	return False

		return True

	def find_trigger(expression, scope):
		for trigger in rules:
			# if the trigger is defined for the current scope
			# REQUIRED? scope = properties.get("scope").replace("//", "")
			if re.search(trigger["scope"], scope):
				# validate its statements on the current context
				if Context.check_trigger(trigger, expression):
					return trigger

		return False

	def get_rule(view):

		selection = view.sel()[0]
		position = selection.begin()
		word_region = view.word(position)

		current_scope = view.scope_name(word_region.a)
		context = get_context(view)
		rule = Context.find_rule(context, current_scope)
		if rule:
			# print("\nVALID context", context, "\nVALID rule:", rule)
			return [rule, context]
		return False
