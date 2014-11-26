# [FuzzyFilePath](https://github.com/sagold/FuzzyFilePath)

__Sublime Text Plugin__

Fuzzy search filenames inside your current project directory. Highly customizable.

<img src="https://raw.githubusercontent.com/sagold/FuzzyFilePath/develop/FuzzyFilePathDemo.gif" />
<br />
<em style="display: block; text-align: right;">Basic settings support Html, Css and Javascript, but may be adjusted for every language</em>

## Breaking changes in 0.1.0

- **change** `exclude_folders` items to be matched as regex
- **remove** `extensionsToSuggest`, now being retrieved from scope settings
- **remove** shortcut `super+ctrl+space`
- **remove** option `auto_trigger`
- **remove** option `insertExtension`. Should now be done by `replace_on_insert`
- **change** and extend default scope rules
- **change** absolute paths to start with "/name"
- **change** path prefix (./, ../, /) now overwrites scope settings

## <a name="installation">Installation</a>


### [Package Control](https://sublime.wbond.net/)

After [Package Control installation](https://sublime.wbond.net/installation), restart Sublime Text. Use the Command Palette `cmd+shift+p` (OS X) or `ctrl+shift+p` (Linux/Windows) and search for *Package Control: Install Package*. Wait until Package Control downloaded the latest package list and search for *FuzzyFilePath*.


### [github](https://github.com/sagold/FuzzyFilePath.git)

in `<SublimeConfig>/Packages/` call: `git clone https://github.com/sagold/FuzzyFilePath.git`

__Sublime Text 2__

in `<SublimeConfig>/Packages/FuzzyFilePath/` switch to Sublime Text 2 Branch with: `git checkout st2`



## <a name="usage">Usage</a>

**Filepaths will be suggested if there is a matching [trigger](#configuration_settings_scopes) for the current context** and its property _auto_ is set
to _true_. For a matching [trigger](#configuration_settings_scopes), filepath completions may be forced (ignoring _auto_ property) by the following
shorcuts:

- __`ctrl+alt+space`__ inserts filepaths relative, overriding possible settings
- __`ctrl+shift+space`__ inserts filepaths absolute, overriding possible settings

The current string may modify the suggested filepaths by the following rules:

- `word` suggests all matching files by the type (relative or absolute) as specified in the matched rule
- `./` suggests matching files within the current directory and inserts selection relative
- `../` suggests all matching files and inserts selection relative
- `/folder` suggests all matching files and insert selection absolute

FuzzyFilePath is disabled for single files or files outside the opened folder.

#### Special Characters

If your projects contains filenames with special characters, consider modifying Sublime Texts `word_separators`.

i.e. in AngularJs filenames may start with `$`. In _Sublime Text | Preferences | Settings - User_ redeclare word
separators, removing `$`:
```js
	"word_separators": "./\\()\"'-:,.;<>~!@#%^&*|+=[]{}`~?"
```


## <a name="getting_started">Getting started</a>

### completions are not suggested

Assuming no errors are logged on console, add a minimum scope rule as first item in settings.scopes. Go to
_Sublime Text | Preferences | Package Settings | FuzzyFilePath | Settings - User_ and add

```js
"scopes": [
	{
		"scope": ".",
		"auto": true,
		// add your extensions here:
		"extensions": ["css", "html", "js"]
	}
]
```

This will propose filepaths for the given extensions in all autocompletion requests. To adjust the trigger see
[settings](configuration_settings). To log trigger evaluation, in settings set `"log": true"`.



### absolute filepaths begin in wrong directory

set your `project_directory` either in project settings or user settings to the correct folder. `project_directory`
must be relative to your sublime project directory.


### relative filepaths are not pointing to the correct file

Relative filepaths point from the current file to the selected file. Folders are moved upwards until the target path
is reachable. i.e. in case of css filepaths, the starting path may be relative from the html file importing the styles.

Set `base_directory` in scope rules to point from project_directory to html file. This will always set the starting
path of the trigger to `base_directory`. i.e.




## <a name="configuration">Configuration</a>

The default options - as always - should be set in user-settings:<br />
_Sublime Text | Preferences | Package Settings | FuzzyFilePath | Settings - User_

Project specific settings may be set in _Project | Edit Settings_:
```js
{
	"settings": {
		"FuzzyFilepath": {
			// adjusted settings
		}
	}
}
```


### <a name="configuration_settings">Settings</a>

##### `project_directory`:String
Set project directory for completions ot a sub folder in sublime project folder. This will deny any caching or
completion of folders outside this folder.
i.e. `"project_directory": "dev/src"`


##### `base_directory`:String
Default base directory to use if set in [trigger](#configuration_settings_scopes).
i.e. `"base_directory": "dev/src"` will be used for relative or absolute filepath completions if scope-property
`scope: { "base_directory": true}`.


##### `disable_autocompletions`:Boolean
Whenever Sublime Text queries completion suggestions, FuzzyFilePath will propose filepaths if the current query meets its requirements.
This may conflict with other plugins. Set `"disable_autocompletions": true` to disable this automatic behaviour.


##### `disable_keymap_actions`:Boolean
Set `"disable_keymap_actions": true` to disable all FuzzyFilePath commands triggered by shortcuts. Default shortcut definitions are
found in _Sublime Text | Preferences | Package Settings | FuzzyFilePath | KeyBinding - Default_. This may prevent conflicts with
other plugins.


##### `exclude_folders`:Array
Skips scanning of given folders. This improves performance on startup (read files) and queries (filter file list).
Folders are checked via regex, thus you need to escape all regex characters.
i.e. `"exclude_folders": ["node\\_modules]` will ignore all files and folders in _node\_modules_ (highly recommended).


#### `scopes`:Array

Each object in `scopes` triggers a specific configuration for filepaths completions. Objects are iterated in the given
order for the current `scope`-regex. If it matches the current scope, its configuration is used for filepath suggestions
and insertions. i.e.
```js
	"scopes": [
		{
			// trigger
		},
		{
			// next trigger
		}
	]
```
Trigger properties are as follows:


#### <a name="configuration_settings_scopes">trigger</a>

##### `scope`:RegExp
A regular expression to test the current scope. In order to escape a regex character two backslashes are required: `\\.`.
To lookup a scope within your source code, press `alt+super+p`. The current scope will be displayed in Sublime Text's
status bar.

i.e. The following rule will apply for strings in javascript scope
```js
	// trigger
	{
		"scope": "string.*\\.js"
	}
```


##### `prefix`:Array, `style`:Array, `tagName`:Array
The scope selection may be further restricted by theese properties. Since scope settings are not easily adjusted,
following variables are retrieved from the current context (cursor position and line):

- The **prefix** is any string before the matched query. Mostly any string before an `=`, `:` or `(`
- The **style** is a string before the prefix, separated by a `:`
- The **tagName** is set with `<tagName ... 'query'`

Examples

- `<img src="./assets/logo.png">` results in `{"prefix": "src", "tagName": "img"}`
- `'"property-name": url(./assets/logo.png)'` results in `{"prefix": "url", "style": "property-name"}` and
- `from 'component'` results in `{"prefix": "from"}`

Any unspecified property will be ignored.


##### `auto`:Boolean
If `"auto": false` the specified configuration will only be triggered by shortcuts.


##### `relative`:Boolean
Sets the type of the path to insert. If `"relative": true` paths will be inserted _relative to the given file_. Else
filepaths are inserted _absolute to the project folder_. This option may also be set by
[key commands for _insert\_path_](#configuration_keybindings). Note: option _relative_ will be overwritten if the string
starts with `/`, `./` or `../`.


##### `base_directory`:Boolean|String
The __base\_directory__ property will adjust the base path from which the filepath is resolved. This is true for
relative and absolute paths. If `"base_directory": true` paths will be resolved from the default __base\_directory__
given in main settings. If `"base_directory": "/dev/src"`, any paths matching this scope-item are resolved by
`/dev/src`.

i.e. if the file in `/dev/src/components/index.js` is inserted absolute, the final path will be
`/components/index.js`


##### <a name="configuration_settings_extensions">`extensions`:Array</a>
This will further filter proposed files for this scope (based on `extensionsToSuggest`).<br />
i.e. `"extensions": ["js", "json"]` will only list javascript or json files.


##### <a name="configuration_settings_replaceoninsert">`replace_on_insert`:Array</a>
An array containing substitutions for the inserted path. After a selected filepath completion is inserted,
the path may be further adjusted. Each item within _replace\_on\_insert_  must be another array like
`[Search:RegExp, Replace:RegExp]`. Use cases:

- If the project path varies, it may be adjusted for the current scope with<br />
	`["\\/base\\_path\\/module", "vendor"]`.
- In NodeJs index files are resolved by default, thus set<br />
	`["index$", ""]` to resolve a selection of _../module/index.js_ to _../module_
- i.e. [webpack](https://github.com/webpack/webpack) may resolve paths differently. Thus if a bower component
	is selected, but its folder is not required, the replacement:<br/>
	`["^[\\.\\./]*/bower_components/", ""]` will fix this.

This option may also be set by [key commands for _insert\_path_](#configuration_keybindings).


#### Example
See _Sublime Text | Preferences | Package Settings | FuzzyFilePath | Settings - Default_ for an up to date version

```js
{
	"disable_autocompletions": false,
	"disable_keymap_actions": false,
	"exclude_folders": ["node\\_modules"],

	"scopes": [
		{
			"scope": "string.*\\.html$",
			// match <div style="background: url(path/to/image)">
			"auto": true,
			"relative": true,
			"base_directory": "path/to/base",
			"extensions": ["png"],
			"prefix": ["url"],
			"style": ["background", "background-image"],
			"tagName": ["div"]
		},
		{
			"scope": "\\.js$",
			// enable shortcuts 'insert_path' for all js languages
			"auto": false,
			"extensions": ["js", "json"],
			"replace_on_insert": [
				["^[\\.\\./]*/bower_components/", ""],
				["index$", ""]
			]
		}
	]
}
```


### <a name="configuration_removed_settings">Removed settings</a>

__extensionsToSuggest:Array__
Valid filetypes are now retrieved from the [extensions](configuration_settings_extensions) property of each _scope_
entry.

__insertExtension:Boolean__
Extensions should now be removed by [replace\_on\_insert](#configuration_settings_replaceoninsert).

__auto_trigger__
removed


### <a name="configuration_keybindings">Keybindings</a>

In addition to automatic filepath suggestions, keybindings may be set to trigger filepath completions, independent of
the current scope. While scope rules will be applied

- the **type** of the requested path (_relative_, _absolute_) may be set explicitly
- the replacements in **replace\_on\_insert** may be overriden
- the base directory for path resolution may be adjusted by **base\_directory** and
- extensions are adjusted by **extensions**

In _Sublime Text | Preferences | KeyBinding - User_ or <br />
_Sublime Text | Preferences | Package Settings | FuzzyFilePath | KeyBinding - Default_ add an object like

```js
{
	"keys": ["ctrl+alt+i"],
	"command": "insert_path"
}
```

This will trigger filepath suggestions on `ctrl+alt+i`, with the current scope rules defined in settings. To override
the _type_ of the path add an arguments object like:

```js
{
	"keys": ["ctrl+alt+i"],
	"command": "insert_path",
	"args": {
	    "type": "relative"
	}
}
```

To override replacements set

```js
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

```js
[
    {
        "keys": ["ctrl+alt+space"],
        "command": "insert_path",
        "args": {
            "type": "relative",
            "base_directory": "dev/src",
            "extensions": ["css", "sass", "less", "png", "gif", "jpg", "svg"]
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





