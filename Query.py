import re, os

from FuzzyFilePath.common.verbose import verbose

class Query:

    auto_trigger = False
    skip_update_replace = False

    def __init__(self):
        self.reset()

    def reset(self):
        self.extensions = ["*"]
        self.relative = False
        self.active = False
        self.extension = True
        self.replace_on_insert = []
        self.skip_update_replace = False


    """ Setup properties for completion query

        Behaviour
        - replaces starting ./ with current folder
        - uses all extensions if completion is triggered and not specified in settings
        - triggers completion if
          - triggered manually
          - scope settings found and auto true OR
          - auto_trigger is set to true and input is path
        - inserts path relative if
          - set in settings and true OR if not false
          - path starts with ../ or ./
          - triggered manually (overrides all)

        Parameters:
        -----------
        current_scope -- complete scope on current cursor position
        needle -- path to search
        force_type -- "default", "relative", "absolute" (default False)
    """
    def build(self, needle, properties, current_folder, force_type=False):
        triggered = force_type is not False

        needle_is_absolute = Query.is_absolute_path(needle)
        needle_is_relative = Query.is_relative_path(needle)
        needle_is_path = needle_is_absolute or needle_is_relative

        if triggered is False and properties["auto"] is False and needle_is_path is False:
            return False

        query_string = Query.get_input_properties(needle, current_folder)

        self.needle = query_string["needle"] # resolved needle for "./" or "../"


        if triggered:
            self.active = True
        else:
            self.active = self.auto_trigger if needle_is_path else properties.get("auto", self.auto_trigger)

        self.extension = properties.get("insertExtension", True)

        self.extensions = properties.get("extensions", ["js"])

        insert_relative = properties.get("relative", query_string["relative"])
        self.relative = Query.get_path_type(insert_relative, current_folder, force_type)

        if not self.skip_update_replace:
            self.replace_on_insert = properties.get("replace_on_insert", [])


        return self.active


    def is_relative_path(needle):
        needle = re.sub("^(./)+", "./", needle)
        return bool(re.match("(\.?\.\/)", needle))

    def is_absolute_path(needle):
        return bool(re.match("\/[A-Za-z0-9\_\-\s\.$]*\/", needle))


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


    def get_input_properties(needle, current_folder):
        properties = {
            "relative": False,
            "needle": needle
        }

        needle = re.sub("^(./)+", "./", needle)

        if needle.startswith("./"):
            properties["relative"] = current_folder
            properties["needle"] = needle.replace("./", current_folder)

        elif needle.startswith("../"):
            properties["relative"] = current_folder
            properties["needle"] = needle.replace("../", "")

        elif re.search("^\/[A-Za-z0-9\_\-\s\.]*\/", needle):
            properties["relative"] = False
            properties["needle"] = needle

        return properties
