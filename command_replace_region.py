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



"""
	<img src="assets/header.png" />
	<div id="inline" style="background-image: url(header.png);">
	background-image: url(header);
	background-image: url('header');
	<script type="text/javascript" src="boot.js">
	<link type="text/css" href="styles.css">
	require("schalalala")
	import "schalalala"
	import schacka
	asdasdalöfkalfdkadlöfsdf
"""

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
		separator = ""
		pre_match = ""
		pre_quotes = re.search("([\"\'\(])([^\"\'\(\)]*)$", pre)
		if pre_quotes:
			# print("pre_quotes: '" + pre_quotes.group(2))
			needle += pre_quotes.group(2) + word
			separator = pre_quotes.group(1)
			pre_match = pre_quotes.group(2)

			post_quotes = re.search("^([^\"\'\)]*)", post)
			if post_quotes:
				# print("post_quotes: '" + post_quotes.group(1))
				needle += post_quotes.group(1)
		else:
			needle = word

		print("needle:'" + needle + "'")
		print("separator:", separator)

		# grab prefix
		prefix_region = sublime.Region(line_region.a, pre_region.b - len(pre_match) - 1)
		prefix_line = view.substr(prefix_region)
		# print("prefix line", prefix_line)


		prefix = re.search("\s*([A-Za-z0-9\-\_]*)[=\s\:\(]*$", prefix_line)
		if prefix:
			print("prefix:", prefix.group(1))

		tag = re.search("<\s*([A-Za-z0-9\-\_]*)\s*[^>]*$", prefix_line)
		if tag:
			tag = tag.group(1)
			print("tag:", tag)

		style = re.search("\s*([A-Za-z0-9\-\_]*)\s*\:[^\:]*$", prefix_line)
		if style:
			style = style.group(1)
			print("style:", style)

