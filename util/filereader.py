import os

def get_absolute_path(filename):
    c_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(c_dir)
    resource_folder = os.path.join(root_dir, 'resources')
    file_path = os.path.join(resource_folder, filename)
    return file_path