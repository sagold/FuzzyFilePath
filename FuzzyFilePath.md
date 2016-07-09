# FuzzyFilePath - autocomplete filepaths

@version 0.2.7
@author Sascha Goldhofer <post@saschagoldhofer.de>


## refactor query

    > keep track of changes and insights through testing (probably needs improvement)

    - make code readable again by improving naming and removing temp variables, duplicates
    - reduce dependencies via properties and decrease messages
    - circular dependencies for completion in ffp and query as module (requires completion)
    - config misbehaviour (scopes: .js) if config is references in module query and module completion
    => 1a. refactor config session object or
    => 1b. resolve circular dependencies ffo controller object (@see refactor event flow)
    => 2. create modules query and completion (temp) until further understanding of those modules (...simplfy)


## tasks

    - growing list of triggers is getting unmaintainable. Probably group by main-scope in object for faster
        retrieval and namespacing
    - add custom triggers without overriding the default scopes
    - support of multiple project folders may be achieved by hooking into settings-folders-array

    - improve testing
    - add to command palette: settings, base_directory
    - test: reload settings on change
