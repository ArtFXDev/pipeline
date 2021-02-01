from engine import Engine
import time
import nuke
from Qt.QtWidgets import QApplication


class NukeEngine(Engine):

    def get_window(self):
        app = QApplication.instance()
        for widget in app.topLevelWidgets():
            if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
                return widget
        return None

    def open(self, path):
        """
        Open file
        """
        path = self.conform(path)
        nuke.scriptOpen(path)

    def open_as(self, path):
        """
        Open file and rename it with a time value
        for keep the source file
        """
        path = self.conform(path)
        nuke.scriptOpen(path)
        nuke.scriptSaveAs(path.replace(
            ".nk", "_{}.nk".format(time.time())))

    def save(self, path):
        """
        Save file as path
        """
        path = self.conform(path)
        print "Save path : " + path
        nuke.scriptSaveAs(path)

    def create_tmp_file(self, sid):
        """
        Create a tmp file to do stuff freely
        :param path: path to save as tmp
        :return str: tmp path to maya scene
        """
        self.save(sid.path)
        tmp_sid = sid.copy()
        tmp_dir = tempfile.gettempdir()
        path_dir = os.path.dirname(self.conform(sid.path))
        path = tmp_sid.path.replace(path_dir, os.path.join(tmp_dir, "artfx"))  # Change to tmp directory
        path = path.replace(".{}".format(tmp_sid.get("ext")), "_{}.{}".format(time.time(), tmp_sid.get("ext")))  # add time-span
        nuke.scriptSaveAs(path)
        self.open(sid.path)
        return path

    def get_file_path(self):
        """
        Get the current file path (from the current open file)
        """
        return nuke.root().knob('name').value()

    def is_batch(self):
        return not nuke.GUI

    def __str__(self):
        """
        Return the soft name
        """
        return 'nuke'


if __name__ == '__main__':
    """
    Test
    """
    # Create engine
    engine = NukeEngine()
    print ("Engine : " + str(engine))
    # Get engine path
    print ("Current file location : " + engine.get_file_path())
    # Save
    engine.save(r"C:\Users\Sylvain\Desktop\test" + engine.get_ext())
    print ("Current file location after save : " + engine.get_file_path())
    # Open as
    engine.open_as(engine.get_file_path())
    print ("Open as ")
    print ("Current file location after open as : " + engine.get_file_path())
    engine.save(engine.get_file_path())
    # Open
    engine.open(r"C:\Users\Sylvain\Desktop\test" + engine.get_ext())
    print ("Current file location after open : " + engine.get_file_path())
