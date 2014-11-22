import re
import os

class Path:

    def sanitize(path):
        # sanitize ././
        path = re.sub("^(./)+", "./", path)
        # sanitize slashes (posix)
        path = path.replace("\\", "/")
        return path

    def is_relative(string):
        return bool(re.match("(\.?\.\/)", string))

    def is_absolute(string):
        return bool(re.match("\/[A-Za-z0-9\_\-\s\.$]*\/", string))

    def get_relative_folder(file_name, base_directory):
        folder = os.path.dirname(file_name)
        folder = os.path.relpath(folder, base_directory)
        folder = "" if folder == "." else folder
        return Path.sanitize(folder)

    def in_project(file_name, folders):
        if file_name is None:
           return False
        if (len(folders) == 0):
           return False
        if (not folders[0] in file_name):
           return False
        return True

