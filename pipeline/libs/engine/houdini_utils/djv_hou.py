import os, hou
from pipeline.tools import engine


def call_djv():
    # get current scene sid, change it for save a png
    current_scene = engine.engine.get()
    current_scene_sid = current_scene.get_sid()
    if not current_scene_sid:
        raise hou.NodeWarning("You project is not in the pipeline")
        return
    current_scene_sid.set(ext="png", frame="$F4")

    # we check if the file_path folder exist
    file_path_folder = os.path.dirname(current_scene_sid.path)
    if not os.path.exists(file_path_folder):
        raise hou.NodeWarning("You have no folder to read")
        return

    # we check if the file_path folder is empty
    if len(os.listdir(file_path_folder)) == 0:
        raise hou.NodeWarning("You have no image to read")
        return

    return file_path_folder


