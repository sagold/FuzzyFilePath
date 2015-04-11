"""
    Validates the current file`s folders based on project folders and its settings.
    Reminder: project = sublime window and opened folder (sidebar)

    Either returns False, if no completions are possible or a dictionary containing required paths and folders of the
    project, file and completion base directory. These folders are required to build the required path completions.
"""
import re
import os
import sublime

import FuzzyFilePath.common.path as Path
from FuzzyFilePath.common.verbose import log


def view(view, config, open_dialog=False):
    """
        returns sanitized directories of current file

        Parameters
        ----
        view : Sublime.View     -- view of current file
        open_dialog: Boolean    -- optional: show directory information in dialog

        return : Dictionary     -- containing evaluted projects path, where
            "project": String       modified project directory from settings:project_directory
            "base": String          relative folder in project from which to resolve paths to files
            "current" : String      relative folder in project directory of current file
    """
    if (file_has_location(view) is False):
        return show_dialog("disabled: file is temporary", open_dialog)

    if (is_project() is False):
        return show_dialog("disabled: not a project", open_dialog)

    directory = project_directory(view, config["PROJECT_DIRECTORY"])
    if directory is False:
        return show_dialog("\ndisabled:{0}<div>not within project directory {1}"
                .format(view.file_name(), config["PROJECT_DIRECTORY"]), open_dialog)

    config["BASE_DIRECTORY"] = sanitize_base_directory(config["BASE_DIRECTORY"], directory["project"], directory["base"])
    directory["current"] = get_current_folder_relative(view, directory["project"])

    if open_dialog is True:
        message = "\nproject directory:\n'{0}'\n".format(directory["project"])
        message += "\nbase directory: '{0}'\n".format(config["BASE_DIRECTORY"])
        message += "\ncurrent directory: '{0}'\n".format(directory["current"])
        show_dialog(message, open_dialog)

    return directory


def get_current_folder_relative(view, project_directory):
    return Path.get_relative_folder(view.file_name(), project_directory)


def file_has_location(view):
    return view.file_name() is not None


def is_project():
    return sublime.active_window().folders() is not None


def get_valid_path(string):
    return re.sub("^[\\\/\.]*", "", string)


def project_directory(view, project_directory):
    """
        Get evaluated project folder of file

        Parameters
        ----
        view : Sublime.View         -- current view/file
        project_directory : String  -- directory of current view

        return : Dictionary         -- False or dictionary with folders as
    """
    directory = {
        "settings": "",     # specific project directory (relative) given in settings
        "base": False,      # basepath of project (absolute)
        "project": False    # final project path extended by settings: project_directory
    }

    if project_directory:
        # strip any path characters up front, else path.join fails
        directory["settings"] = get_valid_path(project_directory)

    file_name = view.file_name()
    for folder in sublime.active_window().folders():
        # find and build current project directory
        directory["project"] = os.path.join(folder, directory["settings"])
        if directory["project"] in file_name:
            is_project_file = True
            directory["base"] = folder
            return directory
            break

    return False


def sanitize_base_directory(base_directory, project_directory, base_project_directory):
    """
        validate possible base directory
    """
    if not base_directory:
        return ""

    base_directory = get_valid_path(base_directory)
    # base_project_directory    | /path/to/sublime/project
    # project_directory         | /path/to/sublime/project/project_directory
    # - path_to_base_directory  | /path/to/sublime/project/base_directory
    # + path_to_base_directory  | /path/to/sublime/project/project_directory/base_directory
    path_to_base_directory = os.path.join(project_directory, base_directory)
    if not os.path.isdir(path_to_base_directory):
        # BASE_DIRECTORY is NOT a valid folder relative to (possibly modified) project_directory
        path_to_base_directory = os.path.join(base_project_directory, base_directory)

        if not os.path.isdir(path_to_base_directory):
            log("Error: setting's base_directory is not a valid directory in project")
            log("=> changing base_directory {0} to ''".format(base_directory))
            return ""

        elif path_to_base_directory in project_directory:
            # change BASE_DIRECTORY to be '' since its outside of project directory
            log("Error: setting's base_directory is within project directory")
            log("=> changing base_directory {0} to ''".format(base_directory))
            return ""

        else:
            # change BASE_DIRECTORY to be relative to modified project directory
            path_to_base_directory = path_to_base_directory.replace(project_directory, "")
            log("Error: setting's base_directory is not relative to project directory")
            log("=> changing base_directory '{0}' to '{1}'".format(base_directory, path_to_base_directory))
            return get_valid_path(path_to_base_directory)

    return base_directory


def show_dialog(message, open=False):
    if open is True:
       header = "FuzzyFilePath\n\n"
       sublime.message_dialog(header + message)
    return False
