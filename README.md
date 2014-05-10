# FuzzyFilePath

__Sublime Text 3 Plugin__

Fuzzy search and autocomplete filenames inside current project directory. Search result may be inserted absolute or relative (i.e. `../../lib/index.js`)

<img src="https://raw.githubusercontent.com/sagold/FuzzyFilePath/master/FuzzyFilePathDemo.gif" />

## Installation

in `<SublimeConfig>/Packages/`

`git clone https://github.com/sagold/FuzzyFilePath.git`


## Usage

Filepath suggestions are only proposed for files within an opened folder. For single files or a files outside the opened folder autocompletion is disabled.
Filepath completions are triggered automatically if defined in settings, else a shortcut is required.

- __`ctrl+super+space`__ inserts default (settings) or absolute filepath completion
- __`ctrl+alt+space`__ inserts filepaths relative, overriding possible settings
- __`ctrl+shift+space`__ inserts filepaths absolute, overriding possible settings

By default `auto_trigger` is set to *true*: If an input starts with `./`, `../` or `/src/j` filepaths will be automatically suggested with the following rules:

- `./` suggests file within the current directory and inserts selection relative
- `../` suggest all files and inserts selection relative
- `/src/j` suggest all files and inserts selection absolute

Search criteria stay the same, but a scope definition in settings overrides the filepath type (*relative*, *absolute*)

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

- [AutoFileName](https://github.com/BoundInCode/AutoFileName)

