"""
    Manage active state of current completion and post cleanup
"""
import re
import sublime
import FuzzyFilePath.expression as Context
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.string import get_diff
import FuzzyFilePath.common.selection as Selection
from FuzzyFilePath.common.verbose import log
from FuzzyFilePath.common.verbose import verbose
import FuzzyFilePath.common.settings as settings
import FuzzyFilePath.current_state as current_state


ID = "Completion"
start_expression = False
scope_cache = {}

state = {
    "active": False,            # completion currently in progress (serve suggestions)
    "onInsert": [],             # substitutions for building final path
    "base_directory": False     # base directory to set for absolute path
}


def start(post_replacements=[]):
    state["replace_on_insert"] = post_replacements
    state["active"] = True


def stop():
    state["active"] = False
    state["base_directory"] = False


def is_active():
    return state.get("active")


def get_filepaths(view, query, current_file):
    global start_expression

    # parse current context, may contain 'is_valid: False'
    start_expression = Context.get_context(view)
    if start_expression["error"] and not query.by_command():
        verbose(ID, "abort - not a valid context")
        return False

    current_scope = Selection.get_scope(view)
    trigger = find_trigger(current_scope, start_expression, query.by_command())

    # currently trigger is required in Query.build
    if trigger is False:
        verbose(ID, "abort - no trigger found")
        return False

    if query.build(start_expression.get("needle"), trigger, current_file.get_directory()) is False:
        # query is valid, but may not be triggered: not forced, no auto-options
        verbose(ID, "abort - no auto trigger found")
        return False

    # remembed the path for `update_inserted_filepath`, query will be reset...
    state["base_directory"] = query.get_post_remove_path()

    return current_state.search_completions(
        query.get_needle(),
        current_file.get_project_directory(),
        query.get_extensions(),
        query.get_base_path()
    )


def find_trigger(current_scope, expression, byCommand=False):
    """ Returns the first trigger matching the given scope and expression """
    triggers = settings.get("TRIGGER")
    if not byCommand:
        # get any triggers that match the requirements and may start automatically
        triggers = get_matching_autotriggers(current_scope, settings.get("TRIGGER"))
    if not bool(triggers):
        verbose(ID, "abort query, no valid scope-regex for current context")
        return False
    # check if one of the triggers match the current context (expression, scope)
    return Context.find_trigger(expression, current_scope, triggers)


def update_inserted_filepath(view, post_remove):
    """ post completion: adjusts inserted filepath """
    expression = Context.get_context(view)
    # diff of previous needle and inserted needle
    diff = get_diff(post_remove, expression["needle"])
    # cleanup string
    result = re.sub("^" + diff["start"], "", expression["needle"])
    # do not replace current word
    if diff["end"] != start_expression["word"]:
        result = re.sub(diff["end"] + "$", "", result)

    # remove path query completely
    result = apply_post_replacements(result, state.get("base_directory"), state.get("replace_on_insert"))
    log("post cleanup path:'", expression.get("needle"), "' ~~> '", result, "'")

    # replace current query with final path
    view.run_command("ffp_replace_region", {
        "a": expression["region"].a,
        "b": expression["region"].b,
        "string": result,
        "move_cursor": True
    })


def get_matching_autotriggers(scope, triggers):
    """ Returns all triggers that match the given scope """
    # get cached evaluation
    result = scope_cache.get(scope)
    if result is None:
        # evaluate triggers on current scope
        result = [trigger for trigger in triggers if trigger.get("auto") and re.search(trigger.get("scope"), scope)]
        # add to cache
        scope_cache[scope] = result if len(result) > 0 else False
        result = scope_cache.get(scope)

    return result


def apply_post_replacements(path, base_directory, replace_on_insert):
    # hack reverse
    path = re.sub(settings.get("ESCAPE_DOLLAR"), "$", path)
    for replace in replace_on_insert:
        path = re.sub(replace[0], replace[1], path)

    if base_directory and path.startswith("/"):
        path = re.sub("^\/" + base_directory, "", path)
        path = Path.sanitize(path)

    return path
