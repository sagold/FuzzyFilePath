# [FuzzyFilePath](https://github.com/sagold/FuzzyFilePath)

__Sublime Text Plugin__

Fuzzy search and autocomplete filenames inside current project directory. Search result may be inserted absolute or relative (i.e. `../../lib/index.js`)

<img src="https://raw.githubusercontent.com/sagold/FuzzyFilePath/master/FuzzyFilePathDemo.gif" />

*Notes*

- check out [`replace\_on\_insert' option](#configuration_settings_replaceoninsert). This might be very helpul in tweaking completions.

---

1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#configuration)
	- [Settings](#configuration_settings)
	- [Keybindings](#configuration_keybindings)

---


## <a name="installation">Installation</a>

### [Package Control](https://sublime.wbond.net/)

After [Package Control installation](https://sublime.wbond.net/installation), restart Sublime Text. Use the Command Palette `cmd+shift+p` (OS X) or `ctrl+shift+p` (Linux/Windows) and search for *Package Control: Install Package*. Wait until Package Control downloaded the latest package list and search for *FuzzyFilePath*.

### [github](https://github.com/sagold/FuzzyFilePath.git)

in `<SublimeConfig>/Packages/` call: <br />
`git clone https://github.com/sagold/FuzzyFilePath.git`

__Sublime Text 2__

in `<SublimeConfig>/Packages/FuzzyFilePath/` switch to Sublime Text 2 Branch with:<br />
`git checkout st2`



## <a name="usage">Usage</a>

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


#### Special Characters

If your projects contains filenames with special characters, consider modifying Sublime Texts `word_separators`.

i.e. in AngularJs filenames may start with `$`. In _Sublime Text | Preferences | Settings - User_ add:
```json
	"word_separators": "./\\()\"'-:,.;<>~!@#%^&*|+=[]{}`~?"
```



## <a name="configuration">Configuration</a>

The default options, as always, should be set in user-settings:<br />
_Sublime Text | Preferences | Package Settings | FuzzyFilePath | Settings - User_


### <a name="configuration_settings">Settings</a>

#### `disable_autocompletions`:Boolean
Whenever Sublime Text queries completion suggestions, FuzzyFilePath will propose filepaths if the current query meets its requirements.
This may conflict with other plugins. Set `"disable_autocompletions": true` to disable this automatic filepath completions.

#### `disable_keymap_actions`:Boolean
Set `"disable_keymap_actions": false` to disables all FuzzyFilePath commands triggered by shortcuts. Default shortcut definitions are
found in _Sublime Text | Preferences | Package Settings | FuzzyFilePath | KeyBinding - Default_. This may prevent conflicts with
other plugins.

#### `extensionsToSuggest`:Array
FuzzyFilePath will only cache and suggest filetypes defined in this array.<br />
i.e. `"extensionsToSuggest": ["gif", "jpg", "jpg", "png"]` will only suggest imagepaths for the given type

#### `auto_trigger`:Boolean
If `"auto_trigger": true`, FuzzyFilePath will trigger autocompletions if the current word starts with

- `../` or
- `./` or
- `/folder/`

completly ignoring current scope.

#### `scopes`:Array
Each object in `scopes` triggers a specific configuration for filepaths completions. Objects are iterated in the given
order for the current `scope`-regex. If it matches the current scope, its configuration is used for filepath suggestions
and insertions. Configuration properties are as follows:

##### scope:RegExp
A regular expression to test the current scope. In order to escape a regex character two backslashes are required: `\\.`.
To lookup a scope within your source code, press `alt+super+p`. The current scope will be displayed in Sublime Text's status bar.

##### auto:Boolean
If `"auto": false` the specified configuration will only be triggered by shortcuts.

##### relative:Boolean
Sets the type of the path to insert. If `"relative": true` paths will be inserted _relative to the given file_. Else
filepaths are inserted _absolute to the project folder_. This option may also be set by [key commands for _insert\_path_](#configuration_keybindings).

##### extensions:Array
This will further filter proposed files for this scope (based on `extensionsToSuggest`).<br />
i.e. `"extensions": ["js", "json"]` will only list javascript or json files.

##### insertExtension:Boolean
If `"insertExtension": false`, files will be inserted without their file extension.<br />
i.e. javascript AMD imports requires `/modules/dummy` to reference `modules/dummy.js`

##### <a name="configuration_settings_replaceoninsert">replace\_on\_insert:Array</a>
An array containing substitutions for the inserted path. After a selected filepath completion is inserted,
the path may be further adjusted. Each item within _replace\_on\_insert_  must be another array like
`[Search:RegExp, Replace:RegExp]`. Use cases:

- If the project path varies, it may be adjusted for the current scope with<br />
	`["/base_path/module", "module"]`.
- In NodeJs index files are resolved by default, thus set<br />
	`["/index$", ""]` if `"insertExtension": false` to resolve a selection of _../module/index.js_ to _../module_
- i.e. [webpack](https://github.com/webpack/webpack) may resolve paths differently. Thus if a bower component
	is selected, but its folder is not required, the replacement:<br/>
	`["^[\\.\\./]*/bower_components/", ""]` will fix this.

This option may also be set by [key commands for _insert\_path_](#configuration_keybindings).


#### Example
See _Sublime Text | Preferences | Package Settings | FuzzyFilePath | Settings - Default_ for an up to date version

```json
{
	"disable_autocompletions": false,
	"disable_keymap_actions": false,
	"extensionsToSuggest": ["css", "gif", "html", "jpg", "js", "json", "png"],
	"exclude_folders": ["node_modules"],
	"auto_trigger": true,
	"scopes": [
		{
			"scope": "\\.js\\s",

			"auto": false,
			"extensions": ["js", "json"],
			"insertExtension": true,
			"relative": true,
			"replace_on_insert": [
				["^[\\.\\./]*/bower_components/", ""],
				["/index$", ""]
			]
		}
	]
}
```


### <a name="configuration_keybindings">Keybindings</a>

In addition to automatic filepath suggestions, keybindings may be set to trigger filepath completions, independent of
the current scope. While scope rules will be applied

- the **type** of the requested path (_relative_, _absolute_) may be set explicitly and
- the replacements in **replace\_on\_insert** may be overriden

In _Sublime Text | Preferences | KeyBinding - User_ or <br />
_Sublime Text | Preferences | Package Settings | FuzzyFilePath | KeyBinding - Default_ add an object like

```json
{
	"keys": ["ctrl+alt+i"],
	"command": "insert_path"
}
```

This will trigger filepath suggestions on `ctrl+alt+i`, with the current scope rules defined in settings. To override
the _type_ of the path add an arguments object like:

```json
{
	"keys": ["ctrl+alt+i"],
	"command": "insert_path",
	"args": {
	    "type": "relative"
	}
}
```

To override replacements set

```json
{
    "keys": ["ctrl+shift+space"],
    "command": "insert_path",
    "args": {
        "replace_on_insert": [
        	["^[\\.\\./]*/bower_components/", ""]
        ]
    }
}
```


#### Examples
See _Sublime Text | Preferences | Package Settings | FuzzyFilePath | KeyBinding - Default_ for an up to date version

```json
[
    {
        "keys": ["ctrl+super+space"],
        "command": "insert_path"
    },
    {
        "keys": ["ctrl+alt+space"],
        "command": "insert_path",
        "args": {
            "type": "relative"
        }
    },
    {
        "keys": ["ctrl+shift+space"],
        "command": "insert_path",
        "args": {
            "type": "absolute",
            "replace_on_insert": [
            	["^[\\.\\./]*/bower_components/", ""]
            ]
        }
    }
]
```


#### Related Plugins

##### [AutoFileName](https://github.com/BoundInCode/AutoFileName)

- uses file discovery based on current directory instead of fuzzy search
- adds properties for images in autocompletion description

