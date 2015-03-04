import sublime
import os
import gc
import re
from FuzzyFilePath.common.verbose import verbose
from FuzzyFilePath.common.path import Path
from FuzzyFilePath.project.file_cache import FileCache

ID = "search"
ID_CACHE = "cache"

class ProjectFiles:
    """
        Manages path suggestions by loading, caching and filtering project files. Add folders by
        `add(<path_to_parent_folder>)`
    """

    cache = {}
    valid_extensions = None
    exclude_folders = None

    def update_settings(self, file_extensions, exclude_folders):
        if self.valid_extensions != file_extensions or self.exclude_folders != exclude_folders:
            #rebuild cache
            for folder in self.cache:
                self.cache[folder] = FileCache(exclude_folders, file_extensions, folder)
                self.cache.get(folder).start();
        # store settings
        self.valid_extensions = file_extensions
        self.exclude_folders = exclude_folders

    def search_completions(self, needle, project_folder, valid_extensions, base_path=False):
        """
            retrieves a list of valid completions, containing fuzzy searched needle

            Parameters
            ----------
            needle : string -- to search in files
            project_folder : string -- folder to search in, cached via add
            valid_extensions : array -- list of valid file extensions
            base_path : string -- of current file, creates a relative path if not False
            with_extension : boolean -- insert extension

            return : List -- containing sublime completions
        """
        project_files = self.get_files(project_folder)
        if (project_files is None):
            return False

        # basic: strip any dots
        needle = re.sub("\.\./", "", needle)
        needle = re.sub("\.\/", "", needle)
        # remove starting slash
        needle = re.sub("^\/", "", needle)
        # cleanup
        needle = re.sub('["\'\(\)$]', '', needle)
        # prepare for regex extension string
        needle = re.escape(needle);

        # build search expression
        regex = ".*"
        for i in needle:
            regex += i + ".*"

        verbose(ID, "scan", len(project_files), "files for", needle, valid_extensions);

        # get matching files
        result = []
        for filepath in project_files:
            properties = project_files.get(filepath)
            """
                properties[0] = escaped filename without extension, like "test/mock/project/index"
                properties[1] = file extension, like "html"
                properties[2] = file displayed as suggestion, like 'test/mock/project/index     html'
            """
            if ((properties[1] in valid_extensions or "*" in valid_extensions) and re.match(regex, filepath, re.IGNORECASE)):
                completion = self.get_completion(filepath, properties[2], base_path)
                result.append(completion)

        return (result, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS)


    def get_files(self, folder):
        thread = self.cache.get(folder)
        if (thread is None):
            return None

        return thread.files

    # @return {list} completion
    def get_completion(self, target_path, path_display, base_path=False):
        # absolute path
        if base_path is False:
            # return (path_display, "/" + target_path)
            return (target_path, "/" + target_path)
        # create relative path
        else:
            # return (path_display, Path.trace(base_path, target_path))
            return (target_path, Path.trace(base_path, target_path))

    def add(self, parent_folder):
        """ caches all files within the given folder

            Parameters
            ----------
            parent_folder : string -- of files to cache
        """
        if self.valid_extensions is None:
            return False

        self.update(parent_folder)

    def file_is_cached(self, folder, file_name):
        """ returns False if the given file is not within cache

            Parameters
            ----------
            folder : string -- of project
            file_name : string -- optional, file to test
        """
        name, extension = os.path.splitext(file_name)
        extension = extension[1:]
        if not extension in self.valid_extensions:
            verbose(ID_CACHE, "file to cache has no valid extension", extension)
            return True

        if self.folder_is_cached(folder):
            file_name = file_name.replace(folder + '/', "")
            verbose(ID_CACHE, "check filename", file_name);
            if self.cache.get(folder).files.get(file_name):
                return True

        return False

    def folder_is_cached(self, folder):
        return self.cache.get(folder) and self.cache.get(folder).files

    def rebuild(self):
        # completley rebuilds all cached foldes
        for folder in self.cache:
            gc.collect(self.cache[folder])
            self.cache[folder] = FileCache(self.exclude_folders, self.valid_extensions, folder)
            self.cache.get(folder).start();


    # rebuild folder cache
    def update(self, folder, file_name=None):
        if file_name:
            if (self.file_is_cached(folder, file_name)):
                verbose(ID_CACHE, "abort update cache of file {0}. Already cached".format(file_name))
                return False
        elif self.folder_is_cached(folder):
            verbose(ID_CACHE, "abort update cache of folder {0}. Already cached".format(folder))
            return False

        if self.cache.get("folder"):
            gc.collect(self.cache[folder])
            del self.cache[folder]

        verbose(ID_CACHE, "UPDATE", folder)
        self.cache[folder] = FileCache(self.exclude_folders, self.valid_extensions, folder)
        self.cache.get(folder).start();
        return True
