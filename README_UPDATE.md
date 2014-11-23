

#### by default filepaths are inserted relative to current file

- starting the path with "/" will change insertion to absolute filepaths
- starting the path with "./" will suggest files only within current file's directory
- starting the path with "../" will insert it relative
- starting the path with a letter will check for the _relative_-option in scope-settings
	- setting the scope-rule property `"relative": false` will always insert path _absolute_
	- setting the scope-rule property `"relative": true` will always insert path _relative_
	- else insertion will be relative by default
