# coding=utf-8
import sys
import os
import subprocess
from Qt import QtCompat, __binding__, QtWidgets, QtCore
from Qt.QtWidgets import QMessageBox, QFileDialog
# from PySide2 import QtWidgets
from pipeline import conf
from pathlib2 import Path
from shotgun_api3 import shotgun


#from github import Github

default_open_pic = str(Path.home())

mainPath = os.path.dirname(__file__)
ui_path = os.path.join(mainPath, 'qt', 'bug_tracker.ui')
sys.path.append('//multifct/tools/pipeline/global/packages')


class BugTrackerWindow(QtWidgets.QMainWindow):
    """
    Entity Creation window
    """
    def __init__(self, main_windows=None):
        super(BugTrackerWindow, self).__init__()
        if main_windows:
            self.main_windows = main_windows
            if self.main_windows.tb_pin.isChecked():
                self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        QtCompat.loadUi(ui_path, self)
        self.sg = None
        self.type = 'Bug'
        self.priority = '1'
        self.screenshot = ''
        self.screen_list = []
        self.connect()

        if conf.get('LOGIN'):
            self.input_login.setText(conf.get('LOGIN'))

        ''' Link to Shotgun'''
        self.sg_link.setText('<a href=https://artfx.shotgunstudio.com/page/1144 style="color:#00d1ff;"> Shotgun.com <\\a>')
        self.sg_link.setOpenExternalLinks(True)

        """
        Set shotgun
        """
        self.SERVER_PATH = "https://artfx.shotgunstudio.com"

    def connect(self):
        """
        Connect button action to function
        """
        # Type
        self.rb_idea.clicked.connect(lambda: self.change_type('Feature'))
        self.rb_bug.clicked.connect(lambda: self.change_type('Bug'))
        # Priority
        self.prio_small.clicked.connect(lambda: self.change_prio('1'))
        self.prio_medium.clicked.connect(lambda: self.change_prio('2'))
        self.prio_high.clicked.connect(lambda: self.change_prio('3'))
        # Screenshot
        self.bt_screenshot.clicked.connect(self.attach_screen)
        self.bt_send.clicked.connect(self.send)
        self.btn_delete.clicked.connect(self.deleteItem)

    def deleteItem(self):
        self.attach_list.takeItem(self.attach_list.currentRow())
        del self.screen_list[self.attach_list.currentRow()]

    def change_prio(self, val):
        self.priority = val

    def change_type(self, val):
        self.type = val

    def attach_screen(self):
        self.screenshot = QFileDialog.getOpenFileName(self, 'Open file', default_open_pic + "/Pictures/", "Image files (*.jpg *.png)")[0]
        self.screen_list.append(self.screenshot)

        filename = self.screenshot.split('/')[-1]
        self. attach_list.addItem(filename)

    def send(self):
        """
        Send a shotgun ticket
        """
        if self.input_message.toPlainText() and self.input_object.text() and self.input_login.text() and self.input_password.text():
            # Update LOGIN user conf value and get values
            if not conf.get('LOGIN') or conf.get('LOGIN') != self.input_login.text():
                conf.set('LOGIN', self.input_login.text())
            SHOT_LOGIN = self.input_login.text()
            SHOT_PASS = self.input_password.text()
            message = self.input_message.toPlainText() + '\n project : ' + self.main_windows.sid.project
            titre = self.input_object.text()
            type = self.type
            priority = self.priority
            # Create Ticket
            try:
                # Shotgun login and ticket creation
                self.sg = shotgun.Shotgun(self.SERVER_PATH, login=SHOT_LOGIN, password=SHOT_PASS)
                data = {
                    'project': {'type': 'Project', 'id': 567},
                    'sg_ticket_type': type,
                    'sg_priority': priority,
                    'title': titre,
                    'description': message
                }
                ticket_id = self.sg.create('Ticket', data)
                shotgun_url = "https://artfx.shotgunstudio.com/page/1144#Ticket_{}".format(str(ticket_id['id']))
                # Send Screenshot
                for screenshot in self.screen_list:
                    self.sg.upload("Ticket", ticket_id['id'], screenshot)
                # Success message
                self.success(shotgun_url)
            except Exception as ex:
                self.error(ex.message)
                return -1
        else:
            self.error("You need to enter your shotgun password and a object / message")

    def success(self, shotgun_url=None):
        """
        Success message box
        """
        msg = QMessageBox()
        msg.setTextFormat(QtCore.Qt.TextFormat.RichText)
        msg.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Information)
        print("Your ticket as been seend to open it follow the link : {}".format(shotgun_url))
        msg.setText("This issue as been send ! <br /><a href={}>Open it on shotgun</a>".format(shotgun_url))
        msg.setWindowTitle("Ticket")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.close)
        msg.exec_()

    def error(self, message):
        """
        Error message box
        """
        msg = QMessageBox()
        msg.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ticket")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)
        msg.exec_()


if __name__ == '__main__':
    import sys
    from Qt import QtGui

    app = QtWidgets.QApplication(sys.argv)
    fm = BugTrackerWindow()
    fm.show()
    app.exec_()

