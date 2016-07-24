import sublime
import os
import gc
import re
from FuzzyFilePath.common.verbose import verbose
import FuzzyFilePath.common.path as Path
from FuzzyFilePath.project.FileCacheWorker import FileCacheWorker

ID = "search"
ID_CACHE = "cache"

class FileCache:
    """
        Manages path suggestions by loading, caching and filtering project files. Add folders by
        `add(<path_to_parent_folder>)`
    """

    def __init__(self, file_extensions, exclude_folders, directory):
        self.directory = directory
        self.valid_extensions = file_extensions
        self.exclude_folders = exclude_folders
        self.cache = None

        self.rebuild()

    def update_settings(self, file_extensions, exclude_folders):
        settings_have_changed = self.valid_extensions != file_extensions or self.exclude_folders != exclude_folders
        self.valid_extensions = file_extensions
        self.exclude_folders = exclude_folders
        if settings_have_changed:
            self.rebuild()

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
        project_files = self.cache.files
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
                completion = self.get_completion(filepath, base_path)
                result.append(completion)

        return (result, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS)

    def find_file(self, file_name):
        project_files = self.cache.files
        if (project_files is None):
            return False

        result = []
        file_name_query = ".*" + re.escape(file_name) + ".*"
        for filepath in project_files:
            if re.match(file_name_query, filepath, re.IGNORECASE):
                result.append(filepath)
        return result

    def get_completion(self, target_path, base_path=False):
        if base_path is False:
            # absolute path
            return (target_path, "/" + target_path)
        else:
            # create relative path
            return (target_path, Path.trace(base_path, target_path))

    def file_is_cached(self, file_name):
        """ returns False if the given file is not within cache
            tests files with full path or relative from project directory
        """
        name, extension = os.path.splitext(file_name)
        extension = extension[1:]
        if not extension in self.valid_extensions:
            verbose(ID_CACHE, "file to cache has no valid extension", extension)
            return True

        file_name = re.sub(self.directory, "", file_name)
        return self.cache.get(file_name, False) is not False


    def rebuild(self):
        self.cache = FileCacheWorker(self.exclude_folders, self.valid_extensions, self.directory)
        self.cache.start();
