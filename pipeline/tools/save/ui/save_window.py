import os
from Qt.QtWidgets import QMessageBox
from Qt import QtWidgets, QtCompat, QtGui, QtCore
from Qt.QtGui import QRegExpValidator
from Qt.QtCore import QRegExp
from pipeline.libs.utils.ui import popup_manager as popup
from pipeline.libs.manager.entities import Entities

# TODO A ajoute en conf
file = os.path.dirname(__file__)
ui_path = os.path.join(file, 'qt', 'save.ui')


class SaveWindow(QtWidgets.QMainWindow):
    """
    Entity Save window
    """

    def __init__(self, type, entity=None):
        super(SaveWindow, self).__init__()
        self.entity = entity or Entities()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        QtCompat.loadUi(ui_path, self)  # replaces self.setupUi(self)
        # connect functions to ui
        if type == "save":
            self.bt_save.clicked.connect(self.save)
        else:
            self.bt_save.clicked.connect(self.publish)

        new_sid = self.entity.get_next_version(self.entity.get_engine_sid())
        self.lb_new_version.setText(new_sid.get("version"))
        # self.setStyleSheet('QMainWindow{background-color: darkgray;border: 1px solid black;}')
        # other

        if type == "save":
            self.setWindowTitle("Save file")
        else:
            self.bt_save.setText("PUBLISH")
            self.setWindowTitle("Publish file")

    """
    ==========
    SAVE / PUBLISH
    ==========
    """

    def save(self):
        actual_sid = self.entity.get_engine_sid()
        if not actual_sid.has_a('ext'):
            raise popup.FileNotValid()
        if actual_sid.get('state') == "p":
            raise popup.PopUpError("Publish can't be save !")
        # Ascii ONLY
        regex = QRegExp("[a-z-A-Z_]+")
        validator = QRegExpValidator(regex)
        self.input_tag.setValidator(validator)
        comment = self.input_comment.toPlainText().encode("utf-8").decode('cp1252')
        tag = self.input_tag.text()
        # SAVE
        try:
            new_sid = self.entity.datas.make_new_version(actual_sid, tag, comment)
            self.entity.engine.save(new_sid.path)
        except Exception as ex:
            print(ex)
            raise popup.PopUpError('Error in save process ! \n' + ex.message)
        popup.PopUpInfo('You work actualy on : ' + new_sid.get('version'))
        self.close()

    def publish(self):
        """
        Copy le fichier tmp du pre publish et le met dans une nouvelle version publish
        """
        actual_sid = self.entity.get_engine_sid()
        if not actual_sid.has_a('ext'):
            raise popup.FileNotValid()
        try:
            self.entity.engine.save(actual_sid.path)
            tmp_sid = actual_sid.copy()
            # Ascii ONLY
            regex = QRegExp("[a-z-A-Z_]+")
            validator = QRegExpValidator(regex)
            self.input_tag.setValidator(validator)
            comment = self.input_comment.toPlainText().encode("utf-8").decode('cp1252')
            tag = self.input_tag.text()
            tmp_sid.set('state', 'p')
            sid_publish = self.entity.datas.file_system.create_publish(tmp_sid, tag, comment)
            self.entity.engine.save(sid_publish.path)
            self.entity.engine.pre_publish()
            self.entity.engine.publish()
            self.entity.engine.save(sid_publish.path, writable=False)
            # Update Publish valid
            valid_path = self.entity.datas.file_system.create_publish_valid(sid_publish).path
            self.entity.engine.save(valid_path, writable=False)
            popup.PopUpInfo('Publish succeed')
        except Exception as ex:
            print(ex)
            popup.PopUpError('Error Publish: {}'.format(ex.message))
        finally:
            self.entity.engine.open(actual_sid.path)
            self.close()


if __name__ == '__main__':
    import sys
    from Qt import QtGui

    app = QtWidgets.QApplication(sys.argv)
    fm = SaveWindow()
    fm.setPalette(QtGui.QPalette())
    fm.show()
    app.exec_()
