# -*- coding: utf-8 -*-
import os
import random
import webbrowser
import subprocess  # Open explorer
from Qt import QtCompat, __binding__, QtCore, QtGui
from Qt import QtWidgets
from Qt.QtWidgets import QCheckBox, QTableWidgetItem, QApplication, QInputDialog, QMainWindow
from Qt.QtWidgets import QTableWidget, QHeaderView, QMessageBox, QRadioButton, QDesktopWidget
from Qt.QtGui import QRegExpValidator, QPixmap
from Qt.QtCore import QRegExp, Qt, QPoint
# Utils
from pipeline.libs.utils.pipe_exception import PipeException
from pipeline.libs.utils.ui import popup_manager as popup
from spil.libs.util import log
# Sid
from spil.libs.sid import Sid
from spil.libs.fs.fs import FS
# UI
from pipeline.tools.filemanager.ui import create_UI_window as cw_win
from pipeline.tools.filemanager.ui import conform_UI_window as cow_win
from pipeline.tools.bug_tracker.ui import bug_tracker_window as bt_win
# Conf
from pipeline import conf
from spil.conf import fs_conf
# Entities
from pipeline.libs.manager import entities

if os.getenv("DEV_PIPELINE"):
    log.setLevel(log.DEBUG)
else:
    log.setLevel(log.ERROR)

# Init import values
mainPath = os.path.dirname(__file__)

# Set value
ui_path = os.path.join(mainPath, 'qt', 'Pipeline_IN_OUT_UI.ui')
ui_path_hou = os.path.join(mainPath, 'qt', 'houdini_var.ui')
ui_path_quote = os.path.join(mainPath, 'qt', 'Quote_Summiter.ui')
pin_img = os.path.join(mainPath, 'src', 'pin.png')


class FileManager(QMainWindow):

    cb = QApplication.clipboard()

    def __init__(self, parent=None, sid=None):
        super(FileManager, self).__init__(parent)
        QtCompat.loadUi(ui_path, self)  # self.setupUi(self)
        # Set to shot by default # TODO Reload history
        if sid:
            self.sid = Sid(sid=sid)
        else:
            self.sid = Sid()
        self.entity = entities.Entities()
        self.engine_name = self.entity.get_engine()
        # Clipboard
        self.cb = QApplication.clipboard()
        # Load & init the projects
        self.project_load()
        # Read user conf
        self.read_user_conf()
        self.project_change()
        self.random_quote()
        if conf.get("fm_positionX") and conf.get("fm_positionY"):
            self.center(conf.get("fm_positionX"), conf.get("fm_positionY"))
        else:
            self.center()
        # Connects the buttons callback to their function
        self.connect()
        # Default values
        mode_str = "LOCAL"
        self.isDev = True if os.getenv("DEV_PIPELINE") else False
        if "beta" in os.path.dirname(__file__):
            mode_str = "BETA"
        if "prod" in os.path.dirname(__file__):
            mode_str = "PROD"
        if self.isDev:
            mode_str = "DEV"
        self.setWindowTitle("Pipeline - " + mode_str)
        self.listEnv = []
        self.listState = ['w', 'p', 'r']
        if len(self.sid) == 1:
            self.in_shot_radio_btn.setChecked(True)
            self.type_change('s')
        if self.engine_name == 'engine':
            self.in_houdini_checkbox.setChecked(True)
            self.in_maya_checkbox.setChecked(True)
            self.in_nuke_checkbox.setChecked(True)
        else:
            name_checkbox = "in_" + self.engine_name + "_checkbox"
            self.in_filter_checkboxes_layout.findChildren(
                QCheckBox, name_checkbox)[0].setChecked(True)
        if self.engine_name != 'houdini':
            self.action_houdini_var.setVisible(False)
        if self.engine_name != 'maya':
            self.refer_btn.setVisible(False)
        if self.engine_name == 'houdini':
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.tb_pin.setChecked(True)
        # set out panel
        self.set_out_panel()
        # Set the list 5 Header
        self.in_list_5.setHorizontalHeaderLabels(
            ['Version', 'State', 'Ext', 'Date', 'Size', 'Tag'])
        header = self.in_list_5.horizontalHeader()
        if __binding__ in ("PyQt4", "PySide"):
            header.setResizeMode(3, QHeaderView.ResizeToContents)
            header.setResizeMode(5, QHeaderView.Stretch)
        else:
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.Stretch)
        self.open_new_btn.setText('Open new ' + self.engine_name)
        # LOGO
        self.tb_pin.setIcon(QtGui.QIcon(pin_img))
        pixmap = QPixmap(conf.logo_path)
        self.logo.setOpenExternalLinks(True)
        self.logo.setPixmap(pixmap)
        self.logo.linkActivated.connect(self.open_quote)
        try:
            self.refresh()
        except Exception:
            self.sid = Sid()
            self.read_user_conf()
            self.project_change()

    def connect(self):
        """
        Connect all the controls with function
        """
        # =========== IN ===========
        # Buttons
        self.open_btn.clicked.connect(self.open)
        self.open_new_btn.clicked.connect(self.open_new)
        self.renderfarm_btn.clicked.connect(self.open_renderfarm_direct)
        self.import_btn.clicked.connect(self.import_file)
        self.refer_btn.clicked.connect(self.refer_file)
        self.in_copy_sid_btn.clicked.connect(self.copy_sid)
        self.in_paste_sid_btn.clicked.connect(self.paste_sid)
        self.in_open_explorer_btn.clicked.connect(self.open_explorer)
        self.close_btn.clicked.connect(self.close)
        self.refresh_btn.clicked.connect(self.refresh)
        self.in_open_workspace_btn.clicked.connect(self.open_workspace)
        self.delete_btn.clicked.connect(self.delete)
        self.tb_pin.clicked.connect(self.pin_toggle)
        # Radio Button
        self.in_asset_radio_btn.clicked.connect(
            lambda: self.type_change('a'))
        self.in_shot_radio_btn.clicked.connect(
            lambda: self.type_change('s'))
        # Check Box
        self.in_work_checkbox.stateChanged.connect(self.state_change_work)
        self.in_publish_checkbox.stateChanged.connect(
            self.state_change_publish)
        self.in_release_checkbox.stateChanged.connect(
            self.state_change_release)
        self.in_houdini_checkbox.stateChanged.connect(self.env_change)
        self.in_maya_checkbox.stateChanged.connect(self.env_change)
        self.in_nuke_checkbox.stateChanged.connect(self.env_change)
        # List View
        self.in_list_1.currentItemChanged.connect(self.list1_change)
        self.in_list_2.currentItemChanged.connect(self.list2_change)
        self.in_list_3.currentItemChanged.connect(self.list3_change)
        self.in_list_4.currentItemChanged.connect(self.list4_change)
        self.in_list_5.currentItemChanged.connect(self.list5_change)
        # ComboBox
        self.project_combo_box.currentIndexChanged.connect(self.project_change)
        self.project_combo_box.currentIndexChanged.connect(self.save_user_conf)
        # Input
        self.in_input_sid_lineEdit.returnPressed.connect(self.modify_sid)
        # =========== Out ===========
        # Button
        self.out_copy_sid_btn.clicked.connect(self.copy_sid_out)
        self.out_save_btn.clicked.connect(self.save)
        self.out_save_btn.clicked.connect(self.set_out_panel)
        self.publish_radio_btn.toggled.connect(self.save_type_change)
        # self.out_pre_publish_btn.clicked.connect(self.pre_publish)
        self.out_publish_btn.clicked.connect(self.publish)
        # Tab
        self.tabsframe.currentChanged.connect(self.set_out_panel)

        # ============== Tab ================
        self.actionCreate.triggered.connect(self.open_create)
        self.actionConform.triggered.connect(self.open_conform)
        self.action_send.triggered.connect(self.open_send)
        self.action_houdini_var.triggered.connect(self.open_hou_var)
        self.action_summit_quote.triggered.connect(self.open_quote)
        self.action_doc.triggered.connect(self.open_doc)
        self.action_renderfarm.triggered.connect(self.open_renderfarm)

    def center(self, positionX=None, positionY=None):
        qRect = self.frameGeometry()
        if positionX and positionY:
            qRect.moveTo(positionX, positionY)
        else:
            centerPoint = QDesktopWidget().availableGeometry().center()
            qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())

    def clear_all_lists(self):
        self.in_list_1.clear()
        self.in_list_2.clear()
        self.in_list_3.clear()
        self.in_list_4.clear()
        self.in_list_5.clearContents()

    def set_out_panel(self):
        """
        Set the 'out' panel (ui stuff)
        """
        try:
            self.out_error_label.setText('')

            self.save_name_sep.setVisible(True)
            self.out_save_btn.setEnabled(True)
            # self.out_pre_publish_btn.setEnabled(True)
            # self.out_pre_publish_btn.setVisible(False)
            # self.out_publish_btn.setVisible(False)
            # self.out_publish_btn.setEnabled(False)
            self.out_comments_textEdit.setEnabled(True)
            self.out_tag_line_edit.setEnabled(True)
            self.publish_radio_btn.setEnabled(True)

            self.save_radio_btn.setChecked(True)
            next_version_sid = self.entity.get_next_version()
            current_version_sid = self.entity.get_engine_sid()
            self.out_output_sid_label.setText(str(current_version_sid))
            self.out_version_label.setText(next_version_sid.get('version'))
            self.out_output_sid_label.setText(str(next_version_sid))
            if next_version_sid.is_shot():
                self.out_file_name_label.setText(
                    next_version_sid.seq + '_' + next_version_sid.shot)
            else:
                self.out_file_name_label.setText(
                    next_version_sid.cat + '_' + next_version_sid.name)
            if current_version_sid.has_a('state') and current_version_sid.get('state') == 'p':
                raise Exception.message('Publish can\'t be save')
            if current_version_sid.ext == 'ma':
                self.ext_change.show()
            else:
                self.ext_change.hide()
        except Exception as ex:
            self.out_error_label.setText('INVALID FILE')
            self.out_file_name_label.setText('')
            self.out_version_label.setText('')
            self.save_name_sep.setVisible(False)
            self.out_save_btn.setEnabled(False)
            self.out_comments_textEdit.setEnabled(False)
            self.out_tag_line_edit.setEnabled(False)
            self.publish_radio_btn.setEnabled(False)

    def project_load(self):
        """
        Load all the files
        """
        # Project
        self.project_combo_box.clear()
        self.clear_all_lists()
        # Fill
        projects = self.entity.get_projects()
        self.project_combo_box.addItems(projects)

    """
    ==================
    Gestion des Buttons
    ==================
    """

    # Project
    def project_change(self):
        if self.project_combo_box.currentText():
            self.clear_all_lists()
            project = str(self.project_combo_box.currentText())  # example DEMO
            root_pipe = os.getenv('ROOT_PIPE')
            if root_pipe:
                for serv in ["ana", "tars", "ANA", "TARS"]:
                    if serv in root_pipe:
                        if conf.projects_server[project] != serv.lower():
                            new_serv = conf.projects_server[project].upper() if serv[0].isupper() else conf.projects_server[project]
                            os.environ['ROOT_PIPE'] = root_pipe.replace(serv, new_serv)
                            print("ROOT_PIPE update to : {}".format(os.environ['ROOT_PIPE']))
            for key, value in fs_conf.path_mapping['project'].items():
                if key == project:
                    project = value
            if self.sid == "":
                self.sid = Sid()
            self.sid.project = project
            # self.sid.set('project', project)
            if len(str(self.sid).split('/')) < 2:
                if self.in_shot_radio_btn.isChecked():
                    self.type_change('s')
                elif self.in_asset_radio_btn.isChecked():
                    self.type_change('a')
            self.in_input_sid_lineEdit.setText(str(self.sid))
        else:
            self.clear_all_lists()
            self.sid = ''
            self.project_combo_box.setCurrentIndex(0)

    # Type
    def type_change(self, _type):
        if self.sid.project:
            self.sid = Sid(self.sid.project + '/' + _type)
            self.list1_load()
            self.in_input_sid_lineEdit.setText(str(self.sid))

    # State
    def state_change_work(self):
        if self.in_work_checkbox.isChecked():
            self.listState.append('w')
        else:
            self.listState.remove('w')
        self.list5_load()

    def state_change_publish(self):
        if self.in_publish_checkbox.isChecked():
            self.listState.append('p')
        else:
            self.listState.remove('p')
        self.list5_load()

    def state_change_release(self):
        if self.in_release_checkbox.isChecked():
            self.listState.append('r')
        else:
            self.listState.remove('r')
        self.list5_load()

    # Env / Engine TODO Conf ext_by_soft
    def env_change(self):
        if self.in_houdini_checkbox.checkState() and ('hipnc' not in self.listEnv):
            self.listEnv.append('hipnc')
            self.listEnv.append('hip')
        elif self.in_houdini_checkbox.checkState() == False and ('hipnc' in self.listEnv):
            self.listEnv.remove('hipnc')
            self.listEnv.remove('hip')
        if self.in_maya_checkbox.checkState() and ('ma' not in self.listEnv):
            self.listEnv.append('ma')
            self.listEnv.append('mb')
        elif self.in_maya_checkbox.checkState() == False and ('ma' in self.listEnv):
            self.listEnv.remove('ma')
            self.listEnv.remove('mb')
        if self.in_nuke_checkbox.checkState() and ('nk' not in self.listEnv):
            self.listEnv.append('nk')
        elif self.in_nuke_checkbox.checkState() == False and ('nk' in self.listEnv):
            self.listEnv.remove('nk')

        if len(self.listEnv) == 0:  # if nothing is checked, then we add everything
            self.listEnv.append(".*")
        elif ".*" in self.listEnv:  # else we remove the '.*' symbol from the filter
            self.listEnv.remove(".*")
        # Reload the file list
        if self.sid.has_a('subtask'):
            self.list5_load()

# region Manage list (change / load)

    """
    ==================
       Manage list
    ==================
    """

    # Sequence
    def list1_change(self):
        if self.in_list_1.currentItem():
            if self.sid.is_asset():
                self.sid.cat = self.in_list_1.currentItem().text()
            else:
                self.sid.seq = self.in_list_1.currentItem().text()
            self.list2_load()
        else:
            if self.sid.is_asset():
                self.sid.cat = None
            else:
                self.sid.seq = None
        self.sid = self.sid.get_stripped()
        self.in_input_sid_lineEdit.setText(str(self.sid))

    def list1_load(self):
        sid_temp = self.sid.copy()
        self.clear_all_lists()
        self.sid = sid_temp.copy()
        self.text_description.clear()
        if self.sid.is_asset():
            items = FS.get(self.sid.get_with('cat', '*').get_as('cat'))
            self.in_list_1.addItems([i.cat for i in items])
        else:
            items = FS.get(self.sid.get_with('seq', '*').get_as('seq'))
            self.in_list_1.addItems([i.seq for i in items])

    # Shot
    def list2_change(self):
        if self.in_list_2.currentItem():
            if self.sid.is_asset():
                self.sid.name = self.in_list_2.currentItem().text()
            else:
                self.sid.shot = self.in_list_2.currentItem().text()
            self.list3_load()
        else:
            if self.sid.is_asset():
                self.sid.name = None
            else:
                self.sid.shot = None
        self.sid = self.sid.get_stripped()
        self.in_input_sid_lineEdit.setText(str(self.sid))

    def list2_load(self):
        self.in_list_2.clear()
        self.in_list_3.clear()
        self.in_list_4.clear()
        self.in_list_5.clearContents()
        self.text_description.clear()
        if self.sid.is_asset():
            items = FS.get(self.sid.get_with('name', '*').get_as('name'))
            self.in_list_2.addItems([i.name for i in items])
        else:
            items = FS.get(self.sid.get_with('shot', '*').get_as('shot'))
            self.in_list_2.addItems([i.shot for i in items])

    # Task
    def list3_change(self):
        if self.in_list_3.currentItem():
            self.sid.task = self.in_list_3.currentItem().text()
            self.list4_load()
        else:
            self.sid.task = None
        self.sid = self.sid.get_stripped()
        self.in_input_sid_lineEdit.setText(str(self.sid))

    def list3_load(self):
        self.in_list_3.clear()
        self.in_list_4.clear()
        self.in_list_5.clearContents()
        self.text_description.clear()
        items = FS.get(self.sid.get_with('task', '*').get_as('task'))
        self.in_list_3.addItems([i.task for i in items])

    # SubTask
    def list4_change(self):
        if self.in_list_4.currentItem():
            self.sid.subtask = self.in_list_4.currentItem().text()
            self.list5_load()
        else:
            self.sid.subtask = None
        self.sid = self.sid.get_stripped()
        self.in_input_sid_lineEdit.setText(str(self.sid))

    def list4_load(self):
        self.in_list_4.clear()
        self.in_list_5.setRowCount(0)
        self.text_description.clear()
        items = FS.get(self.sid.get_with('subtask', '*').get_as('subtask'))
        self.in_list_4.addItems([i.subtask for i in items])

    # File
    def list5_change(self):
        if self.in_list_5.currentItem():
            rows = []
            version = self.in_list_5.item(
                self.in_list_5.currentRow(), 0).text()
            state = self.in_list_5.item(self.in_list_5.currentRow(), 1).text()
            ext = self.in_list_5.item(self.in_list_5.currentRow(), 2).text()
            # filename = state + '_' + version
            self.sid.version = version
            self.sid.state = state
            self.sid.ext = ext
            self.list6_load()
        else:
            self.sid.version = None
            self.sid.state = None
        self.in_input_sid_lineEdit.setText(str(self.sid))

    def list5_load(self):
        self.in_list_5.setRowCount(0)
        self.text_description.clear()
        files = FS.get(self.sid.get_with(version='*', state='*', ext='*'))
        for sid in files:
            if sid.ext in self.listEnv and sid.state in self.listState:
                state = sid.state
                version = sid.version
                ext = sid.ext
                tag = self.entity.datas.file_system.get_tag(sid)
                date = self.entity.datas.file_system.get_date(sid)
                size = self.entity.datas.file_system.get_size(sid)
                row_position = self.in_list_5.rowCount()
                self.in_list_5.insertRow(row_position)

                self.in_list_5.setItem(
                    row_position, 0, QTableWidgetItem(version))
                self.in_list_5.setItem(
                    row_position, 1, QTableWidgetItem(state))
                self.in_list_5.setItem(row_position, 2, QTableWidgetItem(ext))
                self.in_list_5.setItem(row_position, 3, QTableWidgetItem(date))
                self.in_list_5.setItem(row_position, 4, QTableWidgetItem(size))
                self.in_list_5.setItem(row_position, 5, QTableWidgetItem(tag))

    def list6_load(self):
        version = self.sid.get_as('state')
        comment_file = os.path.join(version.path, 'comment.txt')
        if os.path.exists(comment_file):
            file = open(comment_file, 'r')
            comment = file.read()
            self.text_description.clear()
            self.text_description.insertPlainText(comment)

# endregion

# region User conf

    """
    ==================
    Gestion User Conf
    ==================
    """

    def save_user_conf(self):
        project = self.project_combo_box.currentText()
        conf.set('project', project)
        log.info('user conf updated : ' + project +
                 ' is now the default project')

    def read_user_conf(self):
        try:
            project = conf.project
        except:
            project = None
        if not project:
            self.project_combo_box.addItem("SELECT A PROJECT")
            project = "SELECT A PROJECT"
        index = self.project_combo_box.findText(project) or 0
        self.sid.set('project', project)
        self.project_combo_box.setCurrentIndex(index)

# endregion

# region Out / In

    """
    ==================
    Gestion des Out/In
    ==================
    """

    def import_file(self):
        log.debug('Import')

    def refer_file(self):
        if not self.sid.has_a('ext'):
            raise popup.FileNotValid()
        default_namespace = None
        if str(self.entity.engine) == "maya":
            default_namespace = self.entity.engine.get_namespace(self.sid)
        if default_namespace:
            namespace, ok = QInputDialog.getText(self, 'Namespace', 'Choose Namespace (Nothing for no namespace)',
                                            QtWidgets.QLineEdit.Normal, default_namespace)
            if ok and namespace == "":
                print("No namespace")
                raise PipeException("No namespace")
                # self.entity.engine.create_reference(self.sid, False)
            if ok and namespace:
                print("You choose namespace : \"{}\"".format(namespace))
                self.entity.engine.create_reference(self.sid, True, namespace)
            else:
                print("Invalid namespace, abort reference")
        else:
            self.entity.engine.create_reference(self.sid)

    def open_new(self):
        """
        open selected file in a new soft
        """
        if not self.sid.has_a('ext'):
            raise popup.FileNotValid()
        webbrowser.open(self.sid.path)

    def open(self):
        """
        open selected file
        """
        if not self.sid.has_a('ext'):
            raise popup.FileNotValid()
        elif self.sid.ext not in conf.ext_by_soft[str(self.engine_name)]:
            webbrowser.open(self.sid.path)
        else:
            try:
                path = self.sid.path
                self.entity.engine.open(path)

                """
                set workspace
                """
                project = ''
                for key, value in fs_conf.path_mapping['project'].items():
                    if value == self.sid.project:
                        project = key
                if str(self.sid).split('/')[1] == 's':
                    workspace_path = conf.shot_workspace_path.format(
                        root=conf.root, project=project, dimension='3d')
                else:
                    workspace_path = conf.asset_workspace_path.format(root=conf.root, project=project,
                                                                      cat=self.sid.cat, name=self.sid.name)
                self.entity.engine.set_workspace(workspace_path)
                log.info('Workspace is set to : ' + workspace_path)
                self.close()
            except Exception as ex:
                log.error(ex)
                raise popup.FileNotValid()

    # A modifier
    def save(self):
        actual_sid = self.entity.get_engine_sid()
        if not actual_sid.has_a('ext'):
            raise popup.FileNotValid()

        # Ascii ONLY
        regex = QRegExp("[a-z-A-Z_]+")
        validator = QRegExpValidator(regex)
        self.out_tag_line_edit.setValidator(validator)
        comment = self.out_comments_textEdit.toPlainText().encode("utf-8").decode('cp1252')
        tag = self.out_tag_line_edit.text()
        if self.save_radio_btn.isChecked():
            # SAVE
            try:
                new_sid = self.entity.datas.make_new_version(
                    actual_sid, tag, comment)
                if self.ext_change.isChecked():
                    new_sid.set('ext', 'mb')
                self.entity.engine.save(new_sid.path)
            except Exception as ex:
                raise popup.PopUpError(
                    'Error in save process ! \n' + ex.message)
            popup.PopUpInfo('You work actualy on : ' + new_sid.get('version'))
            self.sid = new_sid
            self.set_out_panel()
            self.refresh()
            # pop_up.PopUpError('Use only character !' + ex.message)

    def save_type_change(self):
        if self.publish_radio_btn.isChecked():
            new_sid = Sid(sid=self.out_output_sid_label.text())
            new_sid.set('state', 'p')
            version = self.entity.engine.get_sid().get('version')
            new_sid.set('version', self.entity.engine.get_sid().get('version'))
            self.out_version_label.setText(version)
            self.out_output_sid_label.setText(str(new_sid))
            # self.out_pre_publish_btn.setVisible(True)
            self.out_publish_btn.setVisible(True)
            self.out_save_btn.setVisible(False)
        elif self.save_radio_btn.isChecked():
            # self.out_pre_publish_btn.setVisible(False)
            self.out_publish_btn.setVisible(False)
            self.out_save_btn.setVisible(True)
            new_sid = Sid(sid=self.out_output_sid_label.text())
            new_sid.set('state', 'w')
            version = self.entity.datas.file_system.get_next_version(
                self.entity.engine.get_sid()).get('version')
            new_sid.set('version', version)
            self.out_version_label.setText(version)
            self.out_output_sid_label.setText(str(new_sid))

    """
    def pre_publish(self):
        actual_sid = self.entity.get_engine_sid()
        if not actual_sid.has_a('ext'):
            raise popup.FileNotValid()
        self.entity.engine.save(actual_sid.path)
        try:
            actual_sid_tmp = actual_sid.copy()
            # Create tmp file
            tmp_scene = self.entity.engine.create_tmp_file(actual_sid_tmp)
            self.entity.engine.open(tmp_scene)
            # Do modifications
            self.entity.engine.pre_publish()
            self.out_pre_publish_btn.setEnabled(False)
            self.out_publish_btn.setEnabled(True)
        except Exception as ex:
            self.entity.engine.open(actual_sid.path)
            raise popup.PopUpError('Error in pre_publish ! \n' + ex.message)
        finally:
            self.entity.engine.open(actual_sid.path)
    """

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
            self.out_tag_line_edit.setValidator(validator)
            comment = self.out_comments_textEdit.toPlainText().encode("utf-8").decode('cp1252')
            tag = self.out_tag_line_edit.text()
            tmp_sid.set('state', 'p')
            if self.engine_name == 'maya' and self.ext_change.isChecked():
                tmp_sid.set('ext', 'mb')
            sid_publish = self.entity.datas.file_system.create_publish(tmp_sid, tag, comment)
            self.entity.engine.save(sid_publish.path)
            self.entity.engine.pre_publish()
            self.entity.engine.publish()
            self.entity.engine.save(sid_publish.path, writable=False)
            # Update Publish valid
            valid_path = self.entity.datas.file_system.create_publish_valid(sid_publish).path
            self.entity.engine.save(valid_path, writable=False)
            popup.PopUpInfo('Publish succeed')
            self.sid = actual_sid
            self.in_input_sid_lineEdit.setText(str(self.sid))
        except Exception as ex:
            popup.PopUpError('Error Publish: {}'.fomat(ex.message))
        finally:
            self.entity.engine.open(actual_sid.path)
            self.refresh()

    def delete(self):

        project = str(self.sid.project)
        for key, value in fs_conf.path_mapping['project'].items():
            if value == project:
                project = key
        recycle_bin_path = conf.recycle_bin_path.format(project=project)
        confirm = self.confirm_delete(self.sid, recycle_bin_path)
        if confirm:
            if '3d' in self.sid.path:
                self.entity.datas.file_system.move_time(
                    self.sid.path, recycle_bin_path)
                path2d = self.sid.path.replace('3d', '2d')
                self.entity.datas.file_system.move_time(
                    path2d, recycle_bin_path)
            else:
                self.entity.datas.file_system.move_time(
                    self.sid.path, recycle_bin_path)
            last = self.sid.last_key()
            self.sid.set(last, '')
            self.refresh()

    def confirm_delete(self, sid, recycle_bin_path):
        confirm = False
        msg = QMessageBox()
        msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Are you sure you want to delete:\n{}\n and its children ?\n"
                    "\n it can be found in your project recycle bin in:\n {}".format(
                        sid.path, recycle_bin_path))
        msg.setWindowTitle("Delete File")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        rep = msg.exec_()
        if rep == QMessageBox.Yes:
            confirm = True
        if rep == QMessageBox.No:
            confirm = False
        return confirm

    def copy_sid(self):
        log.debug('Sucess copy !')
        self.cb.clear(mode=self.cb.Clipboard)
        self.cb.setText(unicode(self.sid), mode=self.cb.Clipboard)

    def copy_sid_out(self):
        log.debug('Sucess copy !')
        self.cb.clear(mode=self.cb.Clipboard)
        self.cb.setText(unicode(self.out_output_sid_label.text()),
                        mode=self.cb.Clipboard)

    def paste_sid(self):
        sid_paste = self.cb.text(mode=self.cb.Clipboard)
        if sid_paste != str(self.sid):
            try:
                paste_sid = Sid(sid_paste)
                if str(paste_sid):
                    self.in_input_sid_lineEdit.setText(sid_paste)
                    self.sid = Sid(sid_paste)
                    self.refresh()
                else:
                    raise
            except Exception as ex:
                raise popup.Error(ex.message)

    def modify_sid(self):
        words = [
            "ad38eba046ddad64168fcdce082183dc",
            "fa01720f3b0c7fa92eaae1267d7e1eae",
            "192.168.2.123",
            "hackerman",
            "86038238b84787077f626c9c32f43d71",
            "你的文件贼健康～我就说一声没有别的意思",
            "game"
        ]
        datas = self.entity.datas.file_system.get_data_json(conf.quote_path)
        words_used = [data[2] for data in datas]
        for word in words:
            if word in self.in_input_sid_lineEdit.text().split(' ') and word not in words_used:
                self.open_quote(word)
                break
        if Sid(path=self.in_input_sid_lineEdit.text()):
            self.sid = Sid(path=self.in_input_sid_lineEdit.text())
            self.refresh()

    def open_explorer(self):
        path = self.sid.get_stripped().path
        if not path:
            log.warn('No valid path found')
            return
        if os.path.isfile(path):
            path = os.path.dirname(path)
        self.entity.engine.explore(path)

    def open_workspace(self):
        if self.sid:
            if 'scenes' in self.sid.path:
                path = self.sid.path.split('/scenes')[0].replace('/', os.sep)
                subprocess.Popen('explorer ' + path)

# endregion

    def open_create(self):
        for x in self.children():
            if x.objectName() == "CreateWindow":
                x.deleteLater()
        create_file_win = cw_win.CreateWindow(self.entity, self)
        create_file_win.show()

    def open_conform(self):
        for x in self.children():
            if x.objectName() == "ConformWindow":
                x.deleteLater()
        conform_file_win = cow_win.ConformWindow(self.entity, self)
        conform_file_win.show()

    def open_send(self):
        bug_tracker_win = bt_win.BugTrackerWindow(self)
        bug_tracker_win.show()

    def open_hou_var(self):
        win = HoudiniVarWindow(self)
        win.show()

    def open_renderfarm(self):
        if self.engine_name == 'maya':
            from submitter import submitter_maya
            submitter_maya.run(self.entity.get_engine_sid())
        elif self.engine_name == 'nuke':
            from submitter import submitter_nuke
            submitter_nuke.run(self.entity.get_engine_sid())
        elif self.engine_name == 'houdini':
            from submitter import submitter_houdini
            submitter_houdini.run(self.entity.get_engine_sid())

    def open_renderfarm_direct(self):
        if not self.sid.has_a('ext'):
            popup.Error("You need to select a scene to send to the renderfarm")
        from submitter import submitter_engine
        submitter_engine.run(self.sid)

    def open_quote(self, word):
        win = SummitQuoteWindow(self.entity, word, self)
        win.show()

    def open_doc(self):
        webbrowser.open(conf.doc_path)

    def update_view(self):
        log.debug(
            "update_view :: send a signal to update the main windows lists here")
        self.refresh()

    def refresh(self):  # smell, have to found better solution to avoid all these "if" esction self imbriqued
        """
        Refresh all list
        """
        # Project Refresh
        project_conf = ""
        for key, value in fs_conf.path_mapping['project'].items():
            if self.sid.get('project') == value:
                project_conf = key
        index_project = self.project_combo_box.findText(project_conf)
        if index_project != self.project_combo_box.currentIndex():
            self.project_combo_box.setCurrentIndex(index_project)
        # Type Refresh
        if self.sid.is_asset() and not self.in_asset_radio_btn.isChecked():
            self.in_asset_radio_btn.setChecked(True)
            self.in_shot_radio_btn.setChecked(False)
        elif self.sid.is_shot() and not self.in_shot_radio_btn.isChecked():
            self.in_shot_radio_btn.setChecked(True)
            self.in_asset_radio_btn.setChecked(False)
        self.list1_load()
        # list 1 Refresh
        if len(str(self.sid).split('/')) > 2:
            seq = str(self.sid).split('/')[2]
            item = self.in_list_1.findItems(seq, Qt.MatchFlag.MatchContains)[0]
            self.in_list_1.setCurrentItem(item)
            # List 2 Refresh
            if len(str(self.sid).split('/')) > 3:
                shot = str(self.sid).split('/')[3]
                item = self.in_list_2.findItems(
                    shot, Qt.MatchFlag.MatchExactly)[0]
                self.in_list_2.setCurrentItem(item)
                self.list3_load()
                # List 3 Refresh
                if len(str(self.sid).split('/')) > 4:
                    shot = str(self.sid).split('/')[4]
                    item = self.in_list_3.findItems(
                        shot, Qt.MatchFlag.MatchExactly)[0]
                    self.in_list_3.setCurrentItem(item)
                    self.list4_load()
                    # List 4 Refresh
                    if len(str(self.sid).split('/')) > 5:
                        subtask = str(self.sid).split('/')[5]
                        item = self.in_list_4.findItems(
                            subtask, Qt.MatchFlag.MatchExactly)[0]
                        self.in_list_4.setCurrentItem(item)
                        # check if the sid is a file
                        if self.sid.has_a('ext'):
                            name_checkbox = "in_" + \
                                conf.get_soft_by_ext(
                                    self.sid.ext) + "_checkbox"
                            self.in_filter_checkboxes_layout.findChildren(
                                QCheckBox, name_checkbox)[0].setChecked(True)
                            if len(str(self.sid).split('/')) > 6:
                                version = str(self.sid).split('/')[6]
                                listItems = self.in_list_5.findItems(
                                    version, Qt.MatchFlag.MatchExactly)
                                item = listItems[0]
                                self.in_list_5.setCurrentItem(item)
                                self.list6_load()

    def random_quote(self):
        data = self.entity.datas.file_system.get_data_json(conf.quote_path)
        if len(data) == 1:
            index = 0
        else:
            index = random.randrange(0, len(data))
        self.quote_label.setText(data[index][0])
        self.phylosoph_label.setText(data[index][1])

    def pin_toggle(self):
        if self.tb_pin.isChecked():
            self.setWindowFlags(self.windowFlags() |
                                QtCore.Qt.WindowStaysOnTopHint)  # enabled
        else:
            self.setWindowFlags(self.windowFlags() & ~
                                QtCore.Qt.WindowStaysOnTopHint)  # disable
        self.show()

    def closeEvent(self, event):
        # do stuff
        try:
            qRect = self.frameGeometry()
            # print("{} - {}".format(int(qRect.x()), int(qRect.y())))
            conf.set("fm_positionX", qRect.x())
            conf.set("fm_positionY", qRect.y())
            conf.set('last_sid', str(self.sid))
        except Exception as e:
            pass
        self.setParent(None)
        event.accept()


class SummitQuoteWindow(QMainWindow):

    def __init__(self, entity, word, main_windows):
        super(SummitQuoteWindow, self).__init__()
        # setup ui
        if main_windows.tb_pin.isChecked():
            self.setWindowFlags(self.windowFlags() |
                                QtCore.Qt.WindowStaysOnTopHint)
        QtCompat.loadUi(ui_path_quote, self)
        self.summit_btn.clicked.connect(self.summit_quote)
        self.word = word
        self.entity = entity

    def summit_quote(self):
        quote = self.quote_label.text()
        name = self.name_label.text()
        if quote != '' and name != '':
            self.update_json(conf.quote_path, [quote, name, self.word, os.getenv('COMPUTERNAME')])
            self.close()

    def update_json(self, path, data):
        datas = self.entity.datas.file_system.get_data_json(path)
        datas.append(data)
        self.entity.datas.file_system.write_data_json(path, datas)


class HoudiniVarWindow(QtWidgets.QMainWindow):
    def __init__(self, main_windows):
        super(HoudiniVarWindow, self).__init__()
        # setup ui
        if main_windows.tb_pin.isChecked():
            self.setWindowFlags(self.windowFlags() |
                                QtCore.Qt.WindowStaysOnTopHint)
        QtCompat.loadUi(ui_path_hou, self)
        self.houdini_var.setPlainText('Exemple : \n\n'
                                      '$JOB = I:/synologydrive/BREACH/03_work_pipe/02_shot/3d\n\n'
                                      '$WIPCACHE = I:/synologydrive/BREACH/03_work_pipe/03_WIP_CACHE_FX/s010/p010\n\n'
                                      '$PUBCACHE = I:/synologydrive/BREACH/03_work_pipe/04_PUBLISH_CACHE_FX/s010/p010\n\n'
                                      '$ASSET = I:/synologydrive/BREACH/03_work_pipe/01_asset_3d\n\n'
                                      '$SHOT = I:/synologydrive/BREACH/03_work_pipe/02_SHOT/3d\n\n'
                                      '$PNUM = p010   // Seulement pour les shots \n\n'
                                      '$SNUM = s010   // Seulement pour les shots\n\n'
                                      '$ASSET_NAME = dance  // Seulement pour les assets')


if __name__ == '__main__':

    # sid = Sid(path='//wall-e/212/WS_PIPELINE/PROJECTS/DEMO/03_work_pipe/02_shot/3d/scenes/s010')
    # print sid

    from Qt import QtGui

    import sys
    app = QtWidgets.QApplication(sys.argv)
    fm = FileManager()
    fm.setPalette(QtGui.QPalette())
    fm.show()
    app.exec_()
