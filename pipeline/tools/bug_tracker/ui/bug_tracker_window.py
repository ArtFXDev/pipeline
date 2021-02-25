# coding=utf-8
import sys
import os
import subprocess
from Qt import QtCompat, __binding__, QtWidgets, QtCore
from Qt.QtWidgets import QMessageBox, QFileDialog
from PySide2 import QtWidgets
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
        '''Type'''
        self.rb_idea.clicked.connect(lambda: self.change_type('Feature'))
        self.rb_bug.clicked.connect(lambda: self.change_type('Bug'))
        '''Priority'''
        self.prio_small.clicked.connect(lambda: self.change_prio('1'))
        self.prio_medium.clicked.connect(lambda: self.change_prio('2'))
        self.prio_high.clicked.connect(lambda: self.change_prio('3'))
        '''Screenshot'''
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
        self.screenshot = QFileDialog.getOpenFileName(self, 'Open file','C:/Users/Pictures/', "Image files (*.jpg *.png)")[0]
        self.screen_list.append(self.screenshot)

        filename = self.screenshot.split('/')[-1]
        self. attach_list.addItem(filename)

    def send(self):

        if self.input_message.toPlainText() and self.input_object.text() and self.input_login.text() and self.input_password.text():

            """
            Get value
            """

            if not conf.get('LOGIN'):
                conf.set('LOGIN', self.input_login.text())

            SHOT_LOGIN = self.input_login.text()
            SHOT_PASS = self.input_password.text()
            message = self.input_message.toPlainText() + '\n project : ' + self.main_windows.sid.project
            titre = self.input_object.text()
            type = self.type
            priority = self.priority

            '''
            Create Ticket
            '''
            self.sg = shotgun.Shotgun(self.SERVER_PATH, login= SHOT_LOGIN, password=SHOT_PASS)

            data = {
                'project': {'type': 'Project', 'id': 567},
                'sg_ticket_type': type,
                'sg_priority': priority,
                'title': titre,
                'description': message
            }

            ticket_id = self.sg.create('Ticket', data)

            '''
            Send Screenshot
            '''
            for screenshot in self.screen_list:

                self.sg.upload("Ticket", ticket_id['id'], screenshot)

            confirm_btn = QMessageBox.information(None, 'Success', "This issue as been send", QMessageBox.Yes)
            if confirm_btn == QMessageBox.Yes:
                self.close()
            else:
                self.lbl_error.setText('Message invalid or empty !')


if __name__ == '__main__':
    import sys
    from Qt import QtGui

    app = QtWidgets.QApplication(sys.argv)
    fm = BugTrackerWindow()
    fm.show()
    app.exec_()

