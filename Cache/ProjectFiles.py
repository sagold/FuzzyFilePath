import sublime
import os
import re
import threading

##
# stores all files and its fragments within property files
#
class CacheFolder(threading.Thread):

    def __init__(self, exclude_folders, extensions):

        self.exclude_folders = exclude_folders
        self.extensions = extensions
        self.files = None
        threading.Thread.__init__(self)

    ##
    # cache files
    #
    # @param {String} folder    parent folder
    def run(self, folder):
        self.files = self.read(folder)
        print("folder '" + folder + "' cached")

    # returns files in folder
    def read(self, folder, base=None):

        folder_cache = {}
        base = base if base is not None else folder
        ressources = os.listdir(folder)

        for ressource in ressources:

            current_path = os.path.join(folder, ressource)

            if (os.path.isfile(current_path)):

                relative_path = current_path.replace(base, "")
                filename, extension = os.path.splitext(relative_path)
                extension = extension[1:]

                if extension in self.extensions:
                    folder_cache[relative_path] = [filename, extension, filename + "\t" + extension]

            elif (not ressource.startswith('.') and os.path.isdir(current_path)):

                if (not ressource in self.exclude_folders):
                    folder_cache.update(self.read(current_path, base))

        return folder_cache


##
# loads and caches files
#
#   folders are added with add(<path_to_parent_folder>)
#
class ProjectFiles:

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
        needle = re.sub('["\']', '', needle)

        # print("needle", needle)

        # build search expression
        regex = ".*"
        for i in needle:
            regex += i + ".*"

        # get matching files
        result = []
        for file in project_files:

            properties = project_files.get(file)
            if ((properties[1] in valid_extensions or "*" in valid_extensions) and re.match(regex, file, re.IGNORECASE)):

                completion = self.get_completion(file, properties, base_path, with_extension)
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
                return (target[2], target_path)
            else:
                return (target[2], target[0])
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

        # find common folder
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

        return result

    # @param {String} parent_folder of files to cache
    def add(self, parent_folder):

        if self.valid_extensions is None:
            return False

        self.update(parent_folder)

    # @param {String} folder    cached folder
    # @param {String} file_name to search in folder
    # @return {Boolean} true if file is within cache
    def file_is_cached(self, folder, file_name):

        if self.folder_is_cached(folder) and file_name is not None:

            file_name = file_name.replace(folder, "")
            if (self.cache.get(folder).files.get(file_name)):
                return True

        return False

    def folder_is_cached(self, folder):
        return self.cache.get(folder) and self.cache.get(folder).files

    # rebuild folder cache
    def update(self, folder, file_name=None):

        if (self.file_is_cached(folder, file_name)):
            return False

        if self.folder_is_cached(folder):
            del self.cache[folder]

        self.cache[folder] = CacheFolder(self.exclude_folders, self.valid_extensions)
        self.cache.get(folder).run(folder);

        return True
