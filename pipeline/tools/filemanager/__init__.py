import os
from Qt.QtWidgets import QMessageBox

from pipeline.tools.filemanager.ui import file_manager as fm_win
from pipeline import conf
from pipeline.libs.engine import engine
engine = engine.get()


def launch():
    global pipe_win
    # Delete existing ui
    if str(engine) != "engine":
        for x in engine.get_window().children():
            if x.objectName() == "PipelineWindow":
                x.close()

    sid = engine.get_sid()
    cur_sid = ""
    if sid :
        cur_sid = sid 
    elif hasattr(conf,"last_sid"):
        cur_sid = conf.last_sid
    # cur_win = engine.get_window()
    # if cur_sid:
    #     cur_win.setWindowTitle("{} - ({})".format(str(cur_win.windowTitle), str(cur_sid)))
    #and str(engine) == "engine" or str(engine) == "houdini"
    if not cur_sid:
        pipe_win = fm_win.FileManager()
    elif not cur_sid:
        pipe_win = fm_win.FileManager(None)
    elif cur_sid and str(engine) == "engine" or str(engine) == "houdini":  # TODO Check why houdini delete pipelineWin
        pipe_win = fm_win.FileManager(sid=str(cur_sid))
    else:
        pipe_win = fm_win.FileManager(None, str(cur_sid))

    pipe_win.show()

