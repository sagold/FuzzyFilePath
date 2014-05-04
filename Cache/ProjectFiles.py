import sublime
import os
import re


class ProjectFiles:

    cache = {}
    valid_extensions = None
    exclude_folders = ["node_modules"]


    def __init__(self, extensions):

        self.valid_extensions = extensions


    def search_completions(self, needle, project_folder, valid_extensions, base_path=False, with_extension=True):

        project_files = self.cache.get(project_folder)
        if (project_files is None):
            return False

        # basic: strip any dots
        needle = re.sub("\.\./", "", needle)
        needle = re.sub("\.\/", "", needle)
        # cleanup
        needle = re.sub('"', '', needle)
        needle = re.sub('', '', needle)
        # substitute
        # needle = re.sub('\.', '\.', needle)

        print("needle", needle)

        # build search expression
        regex = ".*"
        for i in needle:
            regex += i + ".*"
        # regex = re.compile(regex, re.IGNORECASE)

        # get matching files
        result = []
        for file in project_files:

            properties = project_files.get(file)
            if (properties[1] in valid_extensions and re.match(regex, file, re.IGNORECASE)):

                completion = self.get_completion(file, properties, base_path, with_extension)
                result.append(completion)

        return (result, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS)


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


    def get_relative_path(self, target, base):

        bases = base.split("/")
        targets = target.split("/")
        result = ""
        index = 0

        # step back base, until in same folder
        size = len(bases)

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


    # add a folder to cache
    def add(self, folder):

        if self.valid_extensions is None:
            return False

        if not self.cache.get(folder):
            self.update(folder)


    # rebuild folder cache
    def update(self, folder):

        if self.cache.get(folder) is not None:
            del self.cache[folder]

        self.cache[folder] = self.read(folder)
        print("folder cached", folder)


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

                if extension in self.valid_extensions:
                    folder_cache[relative_path] = [filename, extension, filename + "\t" + extension]

            elif (not ressource.startswith('.') and os.path.isdir(current_path)):

                if (not ressource in self.exclude_folders):
                    folder_cache.update(self.read(current_path, base))

        return folder_cache
