18/05/06

- Add `additional_scopes` list for custom scope extension
- Update edit_settings command
- Add json as valid js extension

17/04/01

- fixed an error while post-replacing inserted filepath, which exited with a broken result

CHANGES

- improved goto-file command by quering a simplified path (webpack ~)
- improved goto-file command to open uncached files if filepath does exist
- filecache worker now includes subfolders defined as project-folder, even if exclude_folders does match them


16/09/10

- support for multiple folders
- bugfixes
- major code simplifications


15/06/07

- fixed project settings to be added on top of default settings
- fixed update settings for modified user settings
- fixed an issue on windows where paths were not inserted relative


15/03

- major refactoring and bugfixes

FEATURES

- open path under cursor
- show popup containing context evaluation information, required to setup triggers (requires Sublime Text build 3073)
- set project specifiv project_directory via command palette
- after completion insertion, move to beginning of next word
- support multiple opened projects (in separate windows)

CHANGES

- improve update of caching
	- update cache on project change
	- update cache window focus
	- add command to rebiuld cache manually
	- update cache if a new file is saved
- improve replacement of current path fragments
- display of file path suggestions will not separate file extension. this allows querying filetype


14/11/23

BREAKING CHANGES

- **change** `exclude_folders` items to be matched as regex
- **remove** `extensionsToSuggest`, now being retrieved from scope settings
- **remove** shortcut `super+ctrl+space`
- **remove** option `auto_trigger`
- **remove** option `insertExtension`. Should now be done by `replace_on_insert`
- **change** and extend default scope rules
- **change** absolute paths to start with "/name"
- **change** path prefix (./, ../, /) now overwrites scope settings

CHANGES

- extend insert\_path command (shortcut) with base\_directory and extensions
- add support for base_directory
- extend scope-rules by tagName, style and prefix
- analyse context of cursor to retrieve tagName, style and prefix
- improve retrieval of query in view
- fix path replacement for files being in root
- stability improvements
- refactorings

14/11/02

- fix bug in instant completions (missing string-cleanup method)
- fix trigger to update cached files
- remove bugged merge of exlude\_folder\_patterns and exlude\_folders. Thus exlude\_folders are always applied
- fix bug in updating cache (triggered for invalid file extensions)
- refactorings

14/10/03

- extend insert\_path command by replace\_on\_insert
- add FuzzyFilePath Package Settings to Sublime Text Menu
- setting replace\_on\_insert
- setting disable\_keymap\_actions
- setting disable_autocompletions
- add integration tests