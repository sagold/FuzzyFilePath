# QueryFilePath

Autocompletes filenames taken from current project directory

## Installation

in `<SublimeConfig>/Packages/`

`git clone gitUrl`

To your Javascript syntax file, add

```xml

<key>patterns</key>
<dict>

	<dict>

	    <key>name</key>
	    <string>require.js</string>
	    <key>comment</key>
	    <string>require("path") - PathCompletion</string>

	    <key>match</key>
	    <string>require\s*\(\s*((["'])([^"]*)(["']))\s*\)</string>

	    <key>captures</key>
	    <dict>
	        <key>1</key>
	        <dict>
	            <key>name</key>
	            <string>string.js</string>
	        </dict>
	        <key>2</key>
	        <dict>
	            <key>name</key>
	            <string>punctuation.definition.string.begin.js</string>
	        </dict>
	        <key>3</key>
	        <dict>
	            <key>name</key>
	            <string>string.quoted.js</string>
	        </dict>
	        <key>4</key>
	        <dict>
	            <key>name</key>
	            <string>punctuation.definition.string.end.js</string>
	        </dict>
	    </dict>
	</dict>

	<!-- ... -->

</dict>
```


## Usage

On an autocomplete panel start typing folders and filename, omitting `.` and `/`

- Autocomplete suggestions in `require("file")` or
- triggered by `ctrl+alt+space` for relative paths
- and `ctrl+shift+space` for absolute paths


## Weirdness

- Characters `.` and `/` are not replaced on autocomplete
	- using the triggers, those characters will be removed (weird)
	- not in require statement. Pay attention to wrong results


