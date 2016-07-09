import re
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.config import config


class Completion:
    """
        Manage active state of completion and post cleanup
    """
    active = False  # completion currently in progress (servce suggestions)
    onInsert = []   # substitutions for building final path
    base_directory = False  # base directory to set for absolute path, enabled by query...

    def start(post_replacements=[]):
        Completion.replaceOnInsert = post_replacements
        Completion.active = True

    def stop():
        Completion.active = False
        # set by query....
        Completion.base_directory = False

    def is_active():
        return Completion.active

    def set_base_directory(directory):
        Completion.base_directory = directory

    def get_final_path(path):
        # hack reverse
        path = re.sub(config["ESCAPE_DOLLAR"], "$", path)
        for replace in Completion.replaceOnInsert:
            path = re.sub(replace[0], replace[1], path)

        if Completion.base_directory and path.startswith("/"):
            path = re.sub("^\/" + Completion.base_directory, "", path)
            path = Path.sanitize(path)

        return path
