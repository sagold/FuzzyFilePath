import sublime
import os
import re
import threading
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.config import config

def posix(path):
    return path.replace("\\", "/")


# stores all files and its fragments within property files
class CacheFolder(threading.Thread):

    def __init__(self, exclude_folders, extensions, folder):
        threading.Thread.__init__(self)

        self.exclude_folders = exclude_folders
        self.extensions = extensions
        self.folder = folder
        self.files = None
        threading.Thread.__init__(self)

    def run(self):
        # cache files in folder
        self.files = self.read(self.folder)
        verbose("caching folder", self.folder, self.files)

    def read(self, folder, base=None):
        """return all files in folder"""
        folder_cache = {}
        base = base if base is not None else folder

        # test ignore expressions on current path
        for test in self.exclude_folders:
            if re.search(test, folder) is not None:
                print("cache", "SKIP", folder)
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

        print ("cached folder", folder, "files: ", len(folder_cache))
        return folder_cache


class ProjectFiles:
    """ loads and caches files
        folders are added with add(<path_to_parent_folder>)
    """
    cache = {}
    valid_extensions = None
    exclude_folders = None

    # @constructor
    # @param {array} file_extensions    to load/suggest
    # @param {array} exclude_folders
    def __init__(self, file_extensions, exclude_folders):

        self.valid_extensions = file_extensions
        self.exclude_folders = exclude_folders

    # retrieves a list of valid completions, containing fuzzy searched needle
    #
    # @param {string} needle            to search in files
    # @param {string} project_folder    folder to search in, cached via add
    # @param {array} valid_extensions
    # @param {string|False} base_path   of current file, creates a relative path if not False
    # @param {boolean} with_extension   insert extension
    # @return {List} containing sublime completions
    def search_completions(self, needle, project_folder, valid_extensions, base_path=False, with_extension=True):
        project_files = self.get_files(project_folder)
        if (project_files is None):
            return False

        # basic: strip any dots
        needle = re.sub("\.\./", "", needle)
        needle = re.sub("\.\/", "", needle)
        # cleanup
        needle = re.sub('["\'\(\)]', '', needle)

        # build search expression
        regex = ".*"
        for i in needle:
            regex += i + ".*"

        print("cache scan", len(project_files), "files for", needle, valid_extensions);

        # get matching files
        result = []
        for file in project_files:
            properties = project_files.get(file)
            """
                properties[0] = escaped filename without extension, like "test/mock/project/index"
                properties[1] = file extension, like "html"
                properties[2] = file displayed as suggestion, like 'test/mock/project/index     html'
            """
            if ((properties[1] in valid_extensions or "*" in valid_extensions) and re.match(regex, file, re.IGNORECASE)):

                completion = self.get_completion(properties[0] + "." + properties[1], properties, base_path, with_extension)
                result.append(completion)

        return (result, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS)


    def get_files(self, folder):
        thread = self.cache.get(folder)
        if (thread is None):
            return None

        return thread.files

    # @return {list} completion
    def get_completion(self, target_path, target, base_path=False, with_extension=True):
        # absolute path
        if base_path is False:
            if with_extension is True:
                return (target[2], "/" + target[0] + "." + target[1])
            else:
                return (target[2], "/" + target[0])
        # create relative path
        else:
            if with_extension is True:
                return (target[2], self.get_relative_path(target_path, base_path))
            else:
                return (target[2], self.get_relative_path(target[0], base_path))

    # return {string} path from base to target
    def get_relative_path(self, target, base):

        bases = base.split("/")
        targets = target.split("/")
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

    def add(self, parent_folder):
        """ caches all files within the given folder

            Parameters
            ----------
            parent_folder : string -- of files to cache
        """
        if self.valid_extensions is None:
            return False

        self.update(parent_folder)

    def file_is_cached(self, folder, file_name=None):
        """ returns False if the given file is not within cache

            Parameters
            ----------
            folder : string -- of project
            file_name : string -- optional, file to test
        """
        if file_name is None:
            return self.folder_is_cached(folder)

        name, extension = os.path.splitext(file_name)
        extension = extension[1:]
        if not extension in self.valid_extensions:
            verbose("cache", "file to cache has no valid extension", extension)
            return True

        if self.folder_is_cached(folder):
            file_name = file_name.replace(folder + '/', "")
            if (self.cache.get(folder).files.get(file_name)):
                return True

        return False

    def folder_is_cached(self, folder):
        return self.cache.get(folder) and self.cache.get(folder).files

    # rebuild folder cache
    def update(self, folder, file_name=None):
        if (self.file_is_cached(folder, file_name)):
            verbose("cache", "already cached", file_name)
            return False

        if self.folder_is_cached(folder):
            verbose("cache", "already cached", folder)
            del self.cache[folder]

        verbose("cache", "cache update", file_name)

        print("updating cache", self.exclude_folders, self.valid_extensions, folder)
        self.cache[folder] = CacheFolder(self.exclude_folders, self.valid_extensions, folder)
        self.cache.get(folder).start();
        return True
