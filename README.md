# QueryFilePath

__Sublime Text 3 Plugin__

Autocompletes filenames inside current project directory. Search result may be inserted absolute or relative (i.e. `../../lib/index.js`)


## Installation

in `<SublimeConfig>/Packages/`

`git clone https://github.com/sagold/QueryFilePath.git`


## Usage

On an autocomplete panel start typing folders and filename, omitting `.` and `/`

- if set, shows automatically
- __`ctrl+super+space`__ inserts default completion
- __`ctrl+alt+space`__ inserts relative paths
- __`ctrl+shift+space`__ inserts absolute paths

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
            "relative": true
        }
    },
    // enforces absolute filepath insertion
    {
        "keys": ["ctrl+shift+space"],
        "command": "insert_path",
        "args": {
            "relative": false
        }
    }
]
```


## Weirdness

- Characters `.` and `/` are not replaced on autocomplete
	- using the triggers, those characters will be removed (weird)
	- not when opening automaticall. Pay attention to wrong results
- Inserts `""` when no scope *string* is found


