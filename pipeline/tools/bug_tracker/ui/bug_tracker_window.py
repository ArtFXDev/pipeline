# coding=utf-8
import sys
import os
import subprocess
from Qt import QtCompat, __binding__, QtWidgets, QtCore
from Qt.QtWidgets import QMessageBox, QFileDialog
from PySide2 import QtWidgets
from pipeline import conf
from pathlib2 import Path
from github import Github

default_open_pic = str(Path.home())

mainPath = os.path.dirname(__file__)
ui_path = os.path.join(mainPath, 'qt', 'bug_tracker.ui')


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
        self.type = 'BUG'
        self.screenshot = ''
        """
        Set GitHub
        """
        g = Github(conf.github_pass)
        self.repo = g.get_repo("ArtFXDev/pipeline")
        self.load()
        self.connect()

    def load(self):
        list_issues = []
        open_issues = self.repo.get_issues(state='open')
        for issue in open_issues:
            name = ''
            for label in issue.labels:
                name = name + '[' + label.name + ']'
            list_issues.append(name + ' ' + issue.title)
        self.list_send.addItems(list_issues)

    def connect(self):
        self.rb_idea.clicked.connect(lambda: self.change_type('IDEA'))
        self.rb_bug.clicked.connect(lambda: self.change_type('BUG'))
        self.bt_screenshot.clicked.connect(self.screen_shot)
        self.bt_send.clicked.connect(self.send)

    def change_type(self, val):
        self.type = val

    def screen_shot(self):
        self.screenshot = QFileDialog.getOpenFileName(self, 'Open file',
                                                      'C:/Users/Pictures/', "Image files (*.jpg *.png)")[0]

    def send(self):
        if self.input_message.toPlainText() and self.input_object.text() and self.input_name.text():
            """
            Image upload
            """
            image = '![SceenShot](' + self.screenshot + ')'

            """
            Get value
            """
            name = self.input_name.text()
            message = self.input_message.toPlainText() + '\nBy ' + name + ' project : ' + self.main_windows.sid.project
            titre = self.input_object.text()
            label = self.repo.get_label(self.type)
            self.repo.create_issue(title=titre, body=message + ' ' + image, labels=[label])
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
