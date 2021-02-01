import hou
import toolutils
from pipeline.libs import engine
import os

def launch():
    # we open the scene
    scene = toolutils.sceneViewer()

    # we create the settings of the flipbook
    settings = scene.flipbookSettings().stash()

    # we create the new output
    current_scene = engine.engine.get()
    current_scene_sid = current_scene.get_sid()
    if not current_scene_sid:
        raise hou.NodeWarning("You project is not in the pipeline")
        return
    current_scene_sid.set(ext="png", frame="$F4")
    print current_scene_sid.path

    # we check if the path already exist, if not we create it
    flipbook_path_save = os.path.dirname(current_scene_sid.path)
    print flipbook_path_save
    flipbook_path_check = os.path.exists(flipbook_path_save)
    if (not flipbook_path_check):
        print "path doesn't exist"
        os.makedirs(flipbook_path_save)
        print "path created"

    # we check if we already have an image
    if (flipbook_path_check and len(os.listdir(flipbook_path_save)) != 0):
        if not hou.ui.displayConfirmation("Overwrite the current flipbook ?"):
            return

    # we set it
    settings.output(current_scene_sid.path)
    settings.frameRange(hou.playbar.playbackRange())

    # we open it
    scene.flipbook(scene.curViewport(), settings)