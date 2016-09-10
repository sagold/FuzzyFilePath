# FuzzyFilePath - autocomplete filepaths

@version 0.2.7
@author Sascha Goldhofer <post@saschagoldhofer.de>


## tasks
	
	- !ensure config is no longer read, use project asettings instead
    - growing list of triggers is getting unmaintainable. Probably group by main-scope in object for faster
        retrieval and namespacing
    - add custom triggers without overriding the default scopes
    - support for multiple project folders may be achieved by hooking into settings-folders-array

    - improve testing
    - add to command palette: settings, base_directory
    - test: reload settings on change
    - possibly send ffp states to serve for better debugging
