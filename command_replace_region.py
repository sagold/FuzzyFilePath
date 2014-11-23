import sublime
import sublime_plugin
from FuzzyFilePath.common.config import config

class FfpReplaceRegionCommand(sublime_plugin.TextCommand):

    # helper: replaces range with string
    def run(self, edit, a, b, string):
        if config["DISABLE_KEYMAP_ACTIONS"] is True:
            return False

        self.view.replace(edit, sublime.Region(a, b), string)
        # print(self.view.command_history(0))



# style, tag, prefix, separator
rules = [
	{
		# html
		"scope": "meta.tag.*string[^\s]*html$",
		# <* src
		"tagName": ["img", "script"],
		"prefix": ["src"],
		"extensions": ["png", "gif", "jpeg", "jpg", "svg"]
	},
	{
		# html
		"scope": "meta\\.tag.*string[^\s]*\\.html",
		# "scope": "html",
		# <link href
		"tagName": ["link"],
		"prefix": ["href"],
		"extensions": ["css"]
	},
	{
		# css
		"scope": "meta\\.property\\-value\\.css",
		# *: url
		"prefix": ["url"],
		"style": ["background-image", "background", "list-type", "list-type-image"],
		"extensions": ["png", "gif", "jpeg", "jpg"]
	},
	{
		# css
		"scope": "meta\\.property\\-value\\.css",
		# src: url
		"prefix": ["url"],
		"style": ["src"],
		"extensions": ["woff", "ttf", "svg"]
	},
	{
		# js
		"scope": "source\\.js",
		# import * from *
		"prefix": ["from", "import"],
		"extensions": ["js"]
	},
	{
		# js
		"scope": "source\\.js.*string",
		# AMD
		"prefix": "define",
		"extensions": ["js"]
	},
	{
		# js
		"scope": "source\\.js.*string",
		# js webpack require: require(*)
		"prefix": ["require"],
		"extensions": ["js", "html", "sass", "css", "less", "png", "gif", "jpg", "jpeg"]
	},
	{
		# js
		"scope": "source\\.js.*string",
		# object.src = *
		"prefix": ["src"],
		"extensions": ["js", "html", "sass", "css", "less", "png", "gif", "jpg", "jpeg"]
	}
]

statements = ["prefix", "tagName", "style"]

def check_rule(rule, result):
	valid = True
	for statement in statements:
		if rule.get(statement) is not None and result.get(statement) is not None and result.get(statement) not in rule.get(statement):
			# print("False for", statement, result.get(statement), "not in", rule.get(statement))
			valid = False

	return valid

def find_rule(result, scope):
	global rules
	for rule in rules:
		if check_rule(rule, result) and re.search(rule["scope"], scope):
			return rule
	return False


"""
	<img src="assets/header.png" />
	<div id="inline" style="background-image: url(header.png);">
	<div id="inline" style="background: #fff url(header.png) repeat-x;">
	background-image: url(header);
	background-image: url('header');
	<script type="text/javascript" src="boot.js">
	<link type="text/css" href="styles.css">
	require("schalalala")
	require(schalalala)
	define(["module/path/to/index", "prefixed/index"], function (module, prefixed) {
	import "schalalala/\in header.png"
	import schacka from schallala/header in.png
	asdasdalöfkalfdkadlöfsdf
	document.getElementById("my-img").src = "dummyimage.com/100x100/eb00eb/fff";
	<div>some text content</div>
	<div>
		some text content
	</div>
"""

NEEDLE_SEPARATOR = "\"\'\(\)"
NEEDLE_SEPARATOR_BEFORE = "\"\'\("
NEEDLE_SEPARATOR_AFTER = "^\"\'\)"
NEEDLE_CHARACTERS = "A-Za-z0-9\-\_$"
NEEDLE_INVALID_CHARACTERS = "\"\'\)=\:\(<>"
DELIMITER = "\s\:\(\[\="


import re
class DebugCommand(sublime_plugin.TextCommand):
	"""
		parse current line to match for
		- current word or path, independendet of selection (but using cursor position)
		- separators around match like: ", ', (
		- prefix of match, like:
			- function name
			- css style propertyName
			- html tagName
	"""
	def run(self, edit):
		view = self.view
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
		print(pre + "|" + word + "|" + post)

		print("\n")

		# grab everything in 'separators'
		needle = ""
		separator = False
		pre_match = ""
		pre_quotes = re.search("(["+NEEDLE_SEPARATOR_BEFORE+"])([^"+NEEDLE_SEPARATOR+"]*)$", pre)
		if pre_quotes:
			# print("pre_quotes: '" + pre_quotes.group(2))
			needle += pre_quotes.group(2) + word
			separator = pre_quotes.group(1)
			pre_match = pre_quotes.group(2)

		else:
			pre_quotes = re.search("(\s)([^"+NEEDLE_SEPARATOR+"\s]*)$", pre)
			if pre_quotes:
				needle = pre_quotes.group(2) + word
				separator = pre_quotes.group(1)
				pre_match = pre_quotes.group(2)

		if pre_quotes:
			post_quotes = re.search("^(["+NEEDLE_SEPARATOR_AFTER+"]*)", post)
			if post_quotes:
				# print("post_quotes: '" + post_quotes.group(1))
				needle += post_quotes.group(1)
			else:
				print("no post quotes found => invalid")
				valid = False
		else:
			needle = word

		print("needle:'" + needle + "'")
		print("separator:", separator)

		# grab prefix
		prefix_region = sublime.Region(line_region.a, pre_region.b - len(pre_match) - 1)
		prefix_line = view.substr(prefix_region)
		# print("prefix line", prefix_line)


		#define? (["...", "..."]) -> before?
		#before: ABC =:([
		# print("prefix line", prefix_line)
		prefix = re.search("\s*(["+NEEDLE_CHARACTERS+"]+)["+DELIMITER+"]*$", prefix_line)
		if prefix is None:
			# validate array, like define(["...", ".CURSOR."])
			prefix = re.search("^\s*(["+NEEDLE_CHARACTERS+"]+)["+DELIMITER+"]+", prefix_line)

		if prefix:
			print("prefix:", prefix.group(1))
			prefix = prefix.group(1)

		tag = re.search("<\s*(["+NEEDLE_CHARACTERS+"]*)\s*[^>]*$", prefix_line)
		if tag:
			tag = tag.group(1)
			print("tag:", tag)

		style = re.search("\s*(["+NEEDLE_CHARACTERS+"]*)\s*\:[^\:]*$", prefix_line)
		if style:
			style = style.group(1)
			print("style:", style)

		if separator is False:
			print("separator undefined => invalid")
			valid = False

		elif re.search("["+NEEDLE_INVALID_CHARACTERS+"]", needle):
			print("invalid characters in needle => invalid")
			valid = False

		elif prefix is None and separator.strip() == "":
			print("prefix undefined => invalid")
			valid = False

		print("valid:", valid)

		if valid is False:
			return False

		result = {
			"needle": needle,
			"valid": valid,
			"prefix": prefix,
			"tagName": tag,
			"style": style
		}

		current_scope = view.scope_name(word_region.a)
		rule = find_rule(result, current_scope)

		if rule:
			print("valid rule AND correct scope", rule, result)

