""" FuzzyFilePath - autocomplete filepaths

    # refactor query

        > keep track of changes and insights through testing (probably needs improvement)

        - make code readable again by improving naming and removing temp variables, duplicates
        - reduce dependencies via properties and decrease messages
        - circular dependencies for completion in ffp and query as module (requires completion)
        - config misbehaviour (scopes: .js) if config is references in module query and module completion
        => 1a. refactor config session object or
        => 1b. resolve circular dependencies ffo controller object (@see refactor event flow)
        => 2. create modules query and completion (temp) until further understanding of those modules (...simplfy)

    # tasks

        - growing list of triggers is getting unmaintainable. Probably group by main-scope in object for faster
            retrieval and namespacing
        - add custom triggers without overriding the default scopes
        - support of multiple project folders may be achieved by hooking into settings-folders-array

        - improve testing
        - add to command palette: settings, base_directory
        - test: reload settings on change


    @version 0.2.7
    @author Sascha Goldhofer <post@saschagoldhofer.de>
"""
import sublime

import re
import os

import FuzzyFilePath.completion as Completion
import FuzzyFilePath.query as Query
import FuzzyFilePath.expression as Context
import FuzzyFilePath.common.selection as Selection
from FuzzyFilePath.project.ProjectManager import ProjectManager
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.verbose import log
from FuzzyFilePath.common.config import config


ID = "FuzzyFilePath"
start_expression = None


def get_matching_autotriggers(scope_cache, scope, triggers):
    # get cached evaluation
    result = scope_cache.get(scope)
    if result is None:
        # evaluate triggers on current scope
        result = [trigger for trigger in triggers if trigger.get("auto") and re.search(trigger.get("scope"), scope)]
        # add to cache
        scope_cache[scope] = result if len(result) > 0 else False
        result = scope_cache.get(scope)

    return result


def get_start_expression():
    print("START EXPR", start_expression)
    return start_expression


def find_trigger(view, scope_cache, expression):
    triggers = config["TRIGGER"]
    current_scope = Selection.get_scope(view)

    if not Query.by_command():
        # get any triggers that match the requirements and may start automatically
        triggers = get_matching_autotriggers(scope_cache, current_scope, config["TRIGGER"])

    if not bool(triggers):
        verbose(ID, "abort query, no valid scope-regex for current context")
        return False

    # check if one of the triggers match the current context (expression, scope)
    return Context.find_trigger(expression, current_scope, triggers)


def get_filepath_completions(scope_cache, view, project_folder, current_folder):
    global Context, Selection, start_expression

    # parse current context, may contain 'is_valid: False'
    expression = Context.get_context(view)
    if expression["error"] and not Query.by_command():
        verbose(ID, "abort not a valid context")
        return False

    trigger = find_trigger(view, scope_cache, expression)

    # currently trigger is required in Query.build
    if trigger is False:
        verbose(ID, "abort completion, no trigger found")
        return False

    if not expression["valid_needle"]:
        word = Selection.get_word(view)
        expression["needle"] = re.sub("[^\.A-Za-z0-9\-\_$]", "", word)
        verbose(ID, "changed invalid needle to {0}".format(expression["needle"]))
    else:
        verbose(ID, "context evaluation {0}".format(expression))

    if Query.build(expression.get("needle"), trigger, current_folder) is False:
        # query is valid, but may not be triggered: not forced, no auto-options
        verbose(ID, "abort valid query: auto trigger disabled")
        return False

    verbose(ID, ".───────────────────────────────────────────────────────────────")
    verbose(ID, "| scope settings: {0}".format(trigger))
    verbose(ID, "| search needle: '{0}'".format(Query.get_needle()))
    verbose(ID, "| in base path: '{0}'".format(Query.get_base_path()))

    start_expression = expression
    completions = ProjectManager.search_completions(
        Query.get_needle(),
        project_folder,
        Query.get_extensions(),
        Query.get_base_path()
    )

    if completions and len(completions[0]) > 0:
        Completion.start(Query.get_replacements())
        view.run_command('_enter_insert_mode') # vintageous
        log("| => {0} completions found".format(len(completions)))
    else:
        sublime.status_message("FFP no filepaths found for '" + Query.get_needle() + "'")
        Completion.stop()
        log("| => no valid files found for needle: {0}".format(Query.get_needle()))

    log("")

    Query.reset()
    return completions


