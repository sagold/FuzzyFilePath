import os
import re


class View():

    def __init__(self, project_directory=False, file_name=False):
        # project directory
        self.project_directory = project_directory
        # directory relative to project
        self.directory = False
        # file does not exist in filesystem
        self.temp = False

        if file_name:
            self.directory = re.sub(project_directory, "", file_name)
            self.directory = re.sub("^[\\\\/\.]*", "", self.directory)
            self.directory = os.path.dirname(self.directory)

    def set_temp(self, is_temp):
        self.temp = is_temp
        return self

    def get_directory(self):
        return self.directory

    def is_temp(self):
        return self.temp

    def get_project_directory(self):
        return self.project_directory