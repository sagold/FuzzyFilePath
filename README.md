# [FuzzyFilePath](https://github.com/sagold/FuzzyFilePath)

__Sublime Text Plugin__

Fuzzy search and autocomplete filenames inside current project directory. Search result may be inserted absolute or relative (i.e. `../../lib/index.js`)

<img src="https://raw.githubusercontent.com/sagold/FuzzyFilePath/master/FuzzyFilePathDemo.gif" />

## Installation

### [Package Control](https://sublime.wbond.net/)

After [Package Control installation](https://sublime.wbond.net/installation), restart Sublime Text. Use the Command Palette `cmd+shift+p` (OS X) or `ctrl+shift+p` (Linux/Windows) and search for *Package Control: Install Package*. Wait until Package Control downloaded the latest package list and search for *FuzzyFilePath*.

### [github](https://github.com/sagold/FuzzyFilePath.git)

in `<SublimeConfig>/Packages/` call: <br />
`git clone https://github.com/sagold/FuzzyFilePath.git`

__Sublime Text 2__

in `<SublimeConfig>/Packages/FuzzyFilePath/` switch to Sublime Text 2 Branch with:<br />
`git checkout st2`

## Usage

Filepath suggestions are only proposed for files within an opened folder.
Autocompletion is disabled for single files or files outside the opened folder.
Filepath completions are triggered automatically if defined in settings, else a shortcut is required.

- __`ctrl+alt+space`__ inserts filepaths relative, overriding possible settings
- __`ctrl+shift+space`__ inserts filepaths absolute, overriding possible settings
- insert default (settings) or absolute filepath completion
	- OS X: __`ctrl+super+space`__
	- Windows/Linux: __`ctrl+alt+shift+space`__


By default `auto_trigger` is set to *true*: If an input starts with `./`, `../` or `/src/j` filepaths will automatically be suggested by the following rules:

- `./` suggests file within the current directory and inserts selection relative
- `../` suggest all files and inserts selection relative
- `/src/j` suggest all files and inserts selection absolute

Search criteria stay the same, but a scope definition in settings will override the filepath type (*relative*, *absolute*)

## Configuration

The default options, as always, should be set in user-settings

#### Settings

in `<SublimeConfig>/Packages/QueryFilePath.sublime-settings`

```json
{
	// file types to cache and suggest
	"extensionsToSuggest": ["css", "gif", "html", "jpg", "js", "json", "md", "png"],

	// folders to skip. Is ignored if project settings exclude folders
	"exclude_folders": ["node_modules"],

	// auto trigger completion if a valid filepath is inserted:
	// ../ or ./ or /word/c
	"auto_trigger": true,

	// enables file completion via scope regexes
	"scopes": [

		// each object is tested on current scope, first match wins
		{
			// tests for ".js " in current scope
			"scope": "\\.js\\s",

			// if matched
			// do not show by default, requires special command to trigger
			"auto": false,
			// show the following extensions only, may be "[*]"
			"extensions": ["js", "json"],
			// insert file with file extension
			"insertExtension": true,
			// insert file relative to current file's directory
			"relative": true
		}
	]
}
```

#### Keybindings

```json
[
	// use relative value from settings
    {
        "keys": ["ctrl+super+space"],
        "command": "insert_path"
    },
    // enforces relative filepath insertion
    {
        "keys": ["ctrl+alt+space"],
        "command": "insert_path",
        "args": {
            "type": "relative"
        }
    },
    // enforces absolute filepath insertion
    {
        "keys": ["ctrl+shift+space"],
        "command": "insert_path",
        "args": {
            "type": "absolute"
        }
    }
]
```


#### Related Plugins

##### [AutoFileName](https://github.com/BoundInCode/AutoFileName)

- uses file discovery based on current directory instead of fuzzy search
- adds properties for images in autocompletion description
- supports Sublime Text 2 and 3

