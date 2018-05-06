# FuzzyFilePath - autocomplete filepaths

@version 0.6.0
@author Sascha Goldhofer <post@saschagoldhofer.de>

## tasks

- possibly create file caches of all project directories simultaneously
- Cleanup @TODO flags
- suddenly Testrunner causes plugin host to expire

### bugs

    - Initial opened view may be falsely recognised as "not within project"

### release

    - WIP: Test changes
    - DONE: Test windows paths
    - Add documentation for multiple folder support

### performance

    - searching in large folders, where the query matches a folder containing many files, are very slow. i.e. searching for "node_modules/path/to/package" is much slower than searching for "path/to/package" (filecount 10k+)
        - current workaround fast_query option in default settings
        - so far the regex can not be improved to be faster and still return the same results, the first step should be to exclude unused folders which (may require an option for folder whitelisting) i.e. "node_modules/(?!szig).*"

### features

    - growing list of triggers is getting unmaintainable
        - Probably group by main-scope in object for faster retrieval and namespacing
        - create an object with ids for a specific trigger and use a list of ids for triggers to use (selecting object)
        - further support trigger objects in the scope-list
    - add custom triggers without overriding the default scopes

### ideas

    - maybe support different triggers based on inserted filepath? (i.e. absolute if matches node_mod...)
    - possibly send ffp states to serve for better debugging
