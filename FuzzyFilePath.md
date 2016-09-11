# FuzzyFilePath - autocomplete filepaths

@version 0.2.7
@author Sascha Goldhofer <post@saschagoldhofer.de>


## tasks

    - cache states where appropriate
    - possibly create file caches of all project directories simultaneously
    - Cleanup @TODO flags

    - growing list of triggers is getting unmaintainable
        - Probably group by main-scope in object for faster retrieval and namespacing
        - create an object with ids for a specific trigger and use a list of ids for triggers to use (selecting object)
    - add custom triggers without overriding the default scopes

    - maybe support different triggers based on inserted filepath? (i.e. absolute if matches node_mod...)
    - suddenly Testrunner causes plugin host to expire
    - test: reload settings on change
    - possibly send ffp states to serve for better debugging
