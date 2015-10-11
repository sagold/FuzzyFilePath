import re
import os

def sanitize(path):
    # sanitize slashes (posix)
    path = posix(path)
    # sanitize ././
    path = re.sub("^\/?(./)+", "./", path)
    path = re.sub("^(\/)+", "/", path)
    return path

def posix(path):
    if path is not None:
        path = path.replace("\\", "/")
    return path

def is_relative(string):
    return bool(re.match("(\.?\.\/)", string))

def is_absolute(string):
    return bool(re.match("\/[A-Za-z0-9\_\-\s\.$]*", string))

def sanitize_base_directory(path):
    path = sanitize(path)
    path = os.path.dirname(path)
    # no leading nor trailing slash
    path = re.sub("^\/*", "", path)
    path = re.sub("\/*$", "", path)
    return path

def get_absolute_path(base_path, relative_path):
    # return absolute target of join(base_path, relative_path)
    # http://stackoverflow.com/questions/17295086/python-joining-current-directory-and-parent-directory-with-os-path-join?rq=1
    path = os.path.join(base_path, relative_path)
    path = os.path.abspath(path)
    return path

def get_relative_folder(file_name, base_directory):
    folder = os.path.dirname(file_name)
    folder = os.path.relpath(folder, base_directory)
    folder = "" if folder == "." else folder
    return sanitize(folder)

# return {string} path from base to target
# !replace with `os.path.relpath(path[, start])`
# => https://docs.python.org/2/library/os.path.html
def trace(from_folder, to_folder):
    if not from_folder:
        return sanitize("./" + to_folder)

    bases = from_folder.split("/")
    targets = to_folder.split("/")
    result = ""
    index = 0

    # step back base, until in same folder
    size = min(len(bases), len(targets))
    while (index < size and bases[index] == targets[index]):
        index += 1

    # strip common folders
    del bases[0:index]
    del targets[0:index]

    if (len(bases) == 0):
        # from base path?
        result = './'
    else:
        result = "../" * len(bases)

    result += "/".join(targets)
    # !Do Debug "//"
    result = re.sub("//", "/", result);

    return result
