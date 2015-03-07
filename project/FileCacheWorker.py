import sublime
import os
import re
import threading
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config
"""
    Scans, parses and stores all files in the given folder to the dictionary `files`

    Each file entry is set by its relative `filepath` and holds an array like
        0 : filename (modified)
        1 : file extension
        2 : sublime text auto completion string
"""
ID = "cache"

def posix(path):
    return path.replace("\\", "/")

# stores all files and its fragments within property files
class FileCacheWorker(threading.Thread):

    def __init__(self, exclude_folders, extensions, folder):
        threading.Thread.__init__(self)

        self.exclude_folders = exclude_folders
        self.extensions = extensions
        self.folder = folder
        self.files = None

    def run(self):
        verbose(ID, "START adding files in", self.folder)
        self.files = self.read(self.folder)
        verbose(ID, len(self.files), "files cached")


    def read(self, folder, base=None):
        """return all files in folder"""
        folder_cache = {}
        base = base if base is not None else folder

        # test ignore expressions on current path
        for test in self.exclude_folders:
            if re.search(test, folder) is not None:
                verbose(ID, "skip " + folder)
                return folder_cache

        # ressources =
        for ressource in os.listdir(folder):
            current_path = os.path.join(folder, ressource)

            if (os.path.isfile(current_path)):

                relative_path = os.path.relpath(current_path, base)
                filename, extension = os.path.splitext(relative_path)
                extension = extension[1:]

                # posix required for windows, else absolute paths are wrong: /asd\ads\
                relative_path = re.sub("\$", config["ESCAPE_DOLLAR"], posix(relative_path))

                if extension in self.extensions:
                    folder_cache[relative_path] = [
                        # modified filepath. $ hack is reversed in post_commit_completion
                        re.sub("\$", config["ESCAPE_DOLLAR"], posix(filename)),
                        # extension of file
                        extension,
                        # sublime completion text
                        posix(filename) + "\t" + extension
                    ]

            elif (not ressource.startswith('.') and os.path.isdir(current_path)):
                folder_cache.update(self.read(current_path, base))

        return folder_cache
