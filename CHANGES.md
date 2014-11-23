14/11/23

BREAKING CHANGES

- **change** `exclude_folders` items to be used as regex
- **remove** `extensionsToSuggest`, now being retrieved from scope settings
- **remove** shortcut `super+ctrl+space`
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
- staility improvements
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