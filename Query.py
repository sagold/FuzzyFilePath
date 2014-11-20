import re, os

from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.path import Path
from FuzzyFilePath.common.config import config

class Query:

    def __init__(self):
        self.reset()

    def reset(self):
        self.extensions = ["*"]
        self.relative = False
        self.replace_on_insert = []
        self.skip_update_replace = False


    def build(self, needle, properties, current_folder, force_type=False):

        triggered = force_type is not False

        needle = Path.sanitize(needle)
        needle_is_absolute = Path.is_absolute(needle)
        needle_is_relative = Path.is_relative(needle)
        needle_is_path = needle_is_absolute or needle_is_relative

        # abort if autocomplete is not available
        if triggered is False and properties["auto"] is False and needle_is_path is False:
            return False

        # determine needle folder
        needle_folder = current_folder if needle_is_relative else False
        needle_folder = properties.get("relative", needle_folder)


        print("REPLACE query", properties.get("replace_on_insert"))

        self.replace_on_insert = self.replace_on_insert if self.skip_update_replace else properties.get("replace_on_insert", [])
        self.relative = Query.get_path_type(needle_folder, current_folder, force_type)
        self.needle = Query.build_needle_query(needle, current_folder)
        self.extensions = properties.get("extensions", ["js"])

        return triggered or (config["AUTO_TRIGGER"] if needle_is_path else properties.get("auto", config["AUTO_TRIGGER"]))


    def build_needle_query(needle, current_folder):
        needle = re.sub("../", "", needle)
        if needle.startswith("./"):
            needle = current_folder + re.sub("\.\/", "", needle)
        return needle


    def get_path_type(relative, current_folder, force_type=False):

        if relative is None:
            relative = False
        elif relative is True:
            relative = current_folder

        # ???
        if force_type is not False and force_type is not "default":
            relative = "relative"

        return relative


    def override_replace_on_insert(self, replacements):
        self.replace_on_insert = replacements
        self.skip_update_replace = True
