import sublime
import os
import re
import threading
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config

def posix(path):
    return path.replace("\\", "/")

# stores all files and its fragments within property files
class FileCache(threading.Thread):

    def __init__(self, exclude_folders, extensions, folder):
        threading.Thread.__init__(self)

        self.exclude_folders = exclude_folders
        self.extensions = extensions
        self.folder = folder
        self.files = None
        threading.Thread.__init__(self)

    def run(self):
        print("FFP UPDATING PROJECTFILES")
        # cache files in folder
        self.files = self.read(self.folder)
        verbose("caching folder", self.folder, self.files)
        print("FFP UPDATING PROJECTFILES DONE", len(self.files))

    def read(self, folder, base=None):
        """return all files in folder"""
        folder_cache = {}
        base = base if base is not None else folder

        # test ignore expressions on current path
        for test in self.exclude_folders:
            if re.search(test, folder) is not None:
                verbose("cache", "SKIP", folder)
                return folder_cache

        # ressources =
        for ressource in os.listdir(folder):
            current_path = os.path.join(folder, ressource)

            if (os.path.isfile(current_path)):

                relative_path = os.path.relpath(current_path, base)
                filename, extension = os.path.splitext(relative_path)
                extension = extension[1:]

                if extension in self.extensions:
                    # $ hack, reversed in post_commit_completion
                    folder_cache[posix(relative_path)] = [re.sub("\$", config["ESCAPE_DOLLAR"], posix(filename)), extension, posix(filename) + "\t" + extension]

            elif (not ressource.startswith('.') and os.path.isdir(current_path)):
                folder_cache.update(self.read(current_path, base))

        verbose("cached folder", folder, "files: ", len(folder_cache))
        return folder_cache
