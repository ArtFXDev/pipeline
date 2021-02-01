from pipeline.tools.save.ui import save_window
from pipeline.libs.utils.ui import popup_manager as popup
from pipeline.libs.manager.entities import Entities


def save():
    # Open In / Out Widget (Save Window)
    entity = Entities()
    actual_sid = entity.get_engine_sid()
    if not actual_sid.has_a('ext'):
        raise popup.PopUpError("Current file invalid (need to be in the pipeline)")
    else:
        save_win = save_window.SaveWindow("save", entity)
        save_win.show()


def publish():
    # Open In / Out Widget (Save Window)
    entity = Entities()
    actual_sid = entity.get_engine_sid()
    if not actual_sid.has_a('ext'):
        raise popup.PopUpError("Current file invalid (need to be in the pipeline)")
    else:
        save_win = save_window.SaveWindow("publish", entity)
        save_win.show()
