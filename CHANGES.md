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