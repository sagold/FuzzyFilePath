def get_project_id(window):
    project_name = window.project_file_name()
    if project_name:
        return project_name
    return window.id()