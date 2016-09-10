# FuzzyFilePath - autocomplete filepaths

@version 0.2.7
@author Sascha Goldhofer <post@saschagoldhofer.de>


## tasks

    - delegate update settings to current_state
    - cache states where appropriate
    - possibly create file caches of all project directories simultaneously
    - Cleanup @TODO flags
    - change project folder config to be used from corresponding folder settings object (additionally...)
    - !ensure config is no longer read, use project settings instead

    - growing list of triggers is getting unmaintainable. Probably group by main-scope in object for faster
        retrieval and namespacing
    - add custom triggers without overriding the default scopes

    - maybe support different triggers based on inserted filepath? (i.e. absolute if matches node_mod...)
    - suddenly Testrunner causes plugin host to expire
    - test: reload settings on change
    - possibly send ffp states to serve for better debugging
