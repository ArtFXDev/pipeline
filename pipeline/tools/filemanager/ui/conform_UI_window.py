import os
# from PySide2 import QtWidgets, QtCore
from Qt.QtWidgets import QMessageBox
from Qt import QtWidgets, QtCompat, QtGui, QtCore
# Utils
from pipeline.libs.utils.pipe_exception import PipeException
from pipeline.libs.utils import log
# Sid
from spil.libs.sid import Sid
from spil.libs.fs.fs import FS
# conf
from pipeline import conf
from spil.conf import fs_conf
from pipeline.libs.manager.entities import Entities

# TODO A ajoute en conf
file = os.path.dirname(__file__)
ui_path = os.path.join(file, 'qt', 'Pipeline_Conform_UI.ui')

# Variables to populate menus :
projects = conf.projects
shot_softwares = conf.shot_softwares
comp_softwares = conf.comp_softwares
asset_categories = ['-- Select a category --']+conf.asset_categories
shot_tasks = ['-- Select a task --']+conf.shot_tasks
asset_tasks = ['-- Select a task --']+conf.asset_tasks
asset_subtasks_dic_full = {'': ('-- Select a subtask --', ''), '-- Select a task --': ('-- Select a subtask --', '')}
asset_subtasks_dic_full.update(conf.asset_subtasks_dic)


class ConformWindow(QtWidgets.QMainWindow):
    """
    Entity Creation window
    """

    def __init__(self, entity=None, main_windows=None):
        super(ConformWindow, self).__init__(main_windows)
        self.main_windows = main_windows
        self.entity = entity or Entities()
        if main_windows:
            if self.main_windows.tb_pin.isChecked():
                self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        QtCompat.loadUi(ui_path, self)  # replaces self.setupUi(self)
        self.center()
        # populate menus
        self.populate_menus()
        # read user conf and set
        self.read_user_conf()
        # CGW
        self.cgw_list_asset = ""
        self.cgw_list_shot = ""
        try:
            self.cgw_list_asset = self.entity.datas.cgw.all_assets_for_project(conf.project)
            self.cgw_list_shot = self.entity.datas.cgw.all_shots_for_project(conf.project)
        except:
            pass
        # connect functions to ui
        self.connect_btn()
        # other
        self.master()
        self.show_shot_layout()
        self.show_asset_layout()
        self.setWindowTitle("Conform file")
        self.shot_radio_btn.setChecked(True)
        # set current software
        index = self.shot_software_combo_box.findText(str(self.entity.engine))
        self.shot_software_combo_box.setCurrentIndex(index)
        # set max length
        seq_combobox_line_edit = self.input_sequence_combo_box.lineEdit()
        seq_combobox_line_edit.setMaxLength(3)
        shot_combobox_line_edit = self.input_shot_combo_box.lineEdit()
        shot_combobox_line_edit.setMaxLength(3)
        self.shot_version.setMaxLength(3)
        self.asset_version.setMaxLength(3)
        # LOGO
        pixmap = QtGui.QPixmap(conf.logo_path)
        self.logo.setPixmap(pixmap)
        self.dropdown_shot_seq()
        self.dropdown_asset_type()

    def populate_menus(self):
        self.input_project_combo_box.clear()
        self.input_project_combo_box.addItems(projects)
        self.input_shot_task_combo_box.clear()
        self.input_shot_task_combo_box.addItems(shot_tasks)
        self.asset_type_combo_box.clear()
        self.asset_type_combo_box.addItems(asset_categories)
        self.input_asset_task_combo_box.clear()
        self.input_asset_task_combo_box.addItems(asset_tasks)
        self.shot_software_combo_box.clear()
        self.shot_software_combo_box.addItems(shot_softwares)
        self.input_asset_subtask_combo_box.clear()
        self.input_asset_subtask_combo_box.addItem('-- Select a subtask --')

    def center(self):
        qRect = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())

    """
    ===========
    Connections
    ===========
    """

    def connect_btn(self):
        self.close_btn.clicked.connect(self.close)
        self.conform_shot_btn.clicked.connect(self.conform_shot)
        self.conform_asset_btn.clicked.connect(self.conform_asset)
        self.input_asset_task_combo_box.currentIndexChanged.connect(self.dropdown_asset_subtask)
        self.input_shot_task_combo_box.currentIndexChanged.connect(self.populate_shot_software)
        self.shot_radio_btn.toggled.connect(self.show_shot_layout)
        self.asset_radio_btn.toggled.connect(self.show_asset_layout)
        self.shot_master_checkbox.stateChanged.connect(self.master)
        self.input_project_combo_box.currentIndexChanged.connect(self.save_user_conf)
        self.shot_version.editingFinished.connect(self.format_shot_version)
        self.asset_version.editingFinished.connect(self.format_asset_version)
        #sequence dropdown format
        seq_combobox_line_edit = self.input_sequence_combo_box.lineEdit()
        seq_combobox_line_edit.editingFinished.connect(self.format_seq_integer)
        #shot dropdown format
        shot_combobox_line_edit = self.input_shot_combo_box.lineEdit()
        shot_combobox_line_edit.editingFinished.connect(self.format_shot_integer)
        #name dropdown format
        name_combobox_line_edit = self.input_asset_name_combo_box.lineEdit()
        name_combobox_line_edit.editingFinished.connect(self.dropdown_asset_task)
        #subtask dropdown format
        subtask_combobox_line_edit = self.input_shot_subtask_combo_box.lineEdit()
        subtask_combobox_line_edit.editingFinished.connect(self.format_subtask)
        #dropdowns
        self.asset_type_combo_box.currentIndexChanged.connect(self.dropdown_asset_name)
        self.input_sequence_combo_box.currentIndexChanged.connect(self.dropdown_shot_shot)
        self.input_shot_task_combo_box.currentIndexChanged.connect(self.dropdown_shot_subtask)

    """
    ==========
    UI Display
    ==========
    """

    def show_shot_layout(self):
        self.asset_frame.hide()
        self.shot_frame.show()

    def master(self):
        shot_combobox_line_edit = self.input_shot_combo_box.lineEdit()
        if self.shot_master_checkbox.isChecked():
            shot_combobox_line_edit.setMaxLength(6)
            shot_combobox_line_edit.setText('master')
            shot_combobox_line_edit.setReadOnly(True)
            self.p_label.setText('')
        else:
            shot_combobox_line_edit.setMaxLength(3)
            shot_combobox_line_edit.setText('')
            shot_combobox_line_edit.setReadOnly(False)
            self.p_label.setText('p')

    def show_asset_layout(self):
        self.shot_frame.hide()
        self.asset_frame.show()
    """
    ===================
    Populate Dropdowns
    ===================
    """
    def dropdown_asset_type(self):
        project = self.input_project_combo_box.currentText()
        project_sid = fs_conf.path_mapping['project'][project]

        dropdown_asset_cat_sid = Sid(data={'project': project_sid})
        items = FS.get(dropdown_asset_cat_sid.get_with('cat', '*').get_as('cat'))
        cats = ['-- Select a category --']
        for item in items:
            cat = item.cat
            cats.append(cat)
        self.asset_type_combo_box.clear()
        self.asset_type_combo_box.addItems(cats)
        if len(items) > 1:
            self.asset_type_combo_box.setCurrentText(cats[1])

    def dropdown_asset_name(self):
        if self.asset_type_combo_box.currentText() != '-- Select a category --':
            project = self.input_project_combo_box.currentText()
            project_sid = fs_conf.path_mapping['project'][project]
            #asset
            cat = self.asset_type_combo_box.currentText()
            name = self.input_asset_name_combo_box.currentText()

            dropdown_asset_name_sid = Sid(data={'project': project_sid, 'cat': cat, 'name': name})
            items = FS.get(dropdown_asset_name_sid.get_with('name', '*').get_as('name'))
            names = ['']
            for item in items:
                name = item.name
                names.append(name)
            if self.cgw_list_asset:
                for asset_cgw in self.cgw_list_asset:
                    if cat in asset_cgw.cat:
                        names.append(asset_cgw.name)
            self.input_asset_name_combo_box.clear()
            self.input_asset_name_combo_box.addItems(names)
            
    def dropdown_shot_seq(self):
        project = self.input_project_combo_box.currentText()
        project_sid = fs_conf.path_mapping['project'][project]

        dropdown_shot_seq_sid = Sid(data={'project': project_sid})
        items = FS.get(dropdown_shot_seq_sid.get_with('seq', '*').get_as('seq'))
        seqs = ['']
        for item in items:
            seq = item.seq.replace('s', '')
            seqs.append(seq)
        if self.cgw_list_shot:
            for shot_cgw in self.cgw_list_shot:
                if seq in shot_cgw.seq:
                    seqs.append(shot_cgw.seq.replace('s', ''))
        self.input_sequence_combo_box.clear()
        self.input_sequence_combo_box.addItems(seqs)
        if len(items) == 1:
            self.input_sequence_combo_box.setCurrentText(seqs[1])

    def dropdown_shot_shot(self):
        project = self.input_project_combo_box.currentText()
        project_sid = fs_conf.path_mapping['project'][project]
        #shot
        sequence = self.input_sequence_combo_box.currentText()

        dropdown_shot_shot_sid = Sid(data={'project': project_sid, 'seq': 's' + sequence})
        items = FS.get(dropdown_shot_shot_sid.get_with('shot', '*').get_as('shot'))
        shots = ['']
        for item in items:
            shot = item.shot.replace('p', '')
            shots.append(shot)
        if self.cgw_list_shot:
            for shot_cgw in self.cgw_list_shot:
                if shot_cgw.has_a('shot'):
                    shots.append(shot_cgw.shot.replace('p', ''))
        self.input_shot_combo_box.clear()
        self.input_shot_combo_box.addItems(shots)
        if len(items) == 1:
            self.input_shot_combo_box.setCurrentText(shots[1])

    def dropdown_asset_task(self):
        project = self.input_project_combo_box.currentText()
        project_sid = fs_conf.path_mapping['project'][project]
        category = self.asset_type_combo_box.currentText()
        name = self.input_asset_name_combo_box.currentText()
        dropdown_asset_task_sid = Sid(data={'project': project_sid, 'cat': category, 'name': name})
        items = FS.get(dropdown_asset_task_sid.get_with('task', '*').get_as('task'))
        tasks = asset_tasks
        for item in items:
            if item.task not in tasks:
                tasks.append(item.task)
        self.input_asset_task_combo_box.clear()
        self.input_asset_task_combo_box.addItems(tasks)
        self.input_asset_task_combo_box.setCurrentText(tasks[0])

    def dropdown_asset_subtask(self):
        project = self.input_project_combo_box.currentText()
        project_sid = fs_conf.path_mapping['project'][project]
        category = self.asset_type_combo_box.currentText()
        name = self.input_asset_name_combo_box.currentText()
        task = self.input_asset_task_combo_box.currentText()
        dropdown_asset_subtask_sid = Sid(data={'project': project_sid, 'cat': category, 'name': name, 'task': task})
        items = FS.get(dropdown_asset_subtask_sid.get_with('subtask', '*').get_as('subtask'))
        subtasks = []
        if task in asset_subtasks_dic_full.keys():
            subtasks = asset_subtasks_dic_full[task]
        for item in items:
            subtask = item.subtask
            if subtask != 'main':
                subtasks.append(subtask)
        self.input_asset_subtask_combo_box.clear()
        self.input_asset_subtask_combo_box.addItems(subtasks)
        self.input_asset_subtask_combo_box.setCurrentText(subtasks[0])

    def dropdown_shot_subtask(self):
        project = self.input_project_combo_box.currentText()
        project_sid = fs_conf.path_mapping['project'][project]
        #shot
        sequence = self.input_sequence_combo_box.currentText()
        shot = self.input_shot_combo_box.currentText()
        task = self.input_shot_task_combo_box.currentText()
        task = task.split('_')[1]

        dropdown_shot_subtask_sid = Sid(data={'project': project_sid, 'seq': 's' + sequence, 'shot': 'p' + shot,
                                'task': task})
        items = FS.get(dropdown_shot_subtask_sid.get_with('subtask', '*').get_as('subtask'))
        subtasks = ['main']
        for item in items:
            subtask = item.subtask
            if subtask != 'main':
                subtasks.append(subtask)
        self.input_shot_subtask_combo_box.clear()
        self.input_shot_subtask_combo_box.addItems(subtasks)
        self.input_shot_subtask_combo_box.setCurrentText(subtasks[0])

    """
    ==========
    Make Masks
    ==========
    """

    def format_seq_integer(self):
        line_edit = self.input_sequence_combo_box.lineEdit()
        number = line_edit.text()
        if number.isdigit():
            if int(number) < 10 and number[0] != '0':
                number = '0' + number
            number = number.ljust(3, '0')
        else:
            number = ''
        line_edit.setText(number)

    def format_shot_integer(self):
        line_edit = self.input_shot_combo_box.lineEdit()
        number = line_edit.text()
        if number == 'master':
            pass
        elif number.isdigit():
            if int(number) < 10 and number[0] != '0':
                number = '0' + number
            number = number.ljust(3, '0')
        else:
            number = ''
        line_edit.setText(number)

    def format_asset_version(self):
        number = self.asset_version.text()
        if number.isdigit():
            number = number.zfill(3)
        else:
            number = ''
        self.asset_version.setText(number)

    def format_shot_version(self):
        number = self.shot_version.text()
        if number.isdigit():
            number = number.zfill(3)
        else:
            number = ''
        self.shot_version.setText(number)

    def format_name(self):
        line_edit = self.input_asset_name_combo_box.lineEdit()
        formated_name = str(line_edit.text())
        line_edit.setText(formated_name)

    def format_subtask(self):
        line_edit = self.input_shot_subtask_combo_box.lineEdit()
        formated_subtask = str(line_edit.text())
        line_edit.setText(formated_subtask)

    """
    ==============
    Populate Menus
    ==============
    """

    # def populate_asset_subtask(self):
    #     task = self.input_asset_task_combo_box.currentText()
    #     self.input_asset_subtask_combo_box.clear()
    #     self.input_asset_subtask_combo_box.addItems(asset_subtasks_dic_full[task])

    def populate_shot_software(self):
        task = self.input_shot_task_combo_box.currentText()
        if task == '06_comp':
            self.shot_software_combo_box.clear()
            self.shot_software_combo_box.addItems(comp_softwares)
        elif task == '04_fx':
            self.shot_software_combo_box.clear()
            self.shot_software_combo_box.addItems(shot_softwares)
            self.shot_software_combo_box.setCurrentText('houdini')
        else:
            self.shot_software_combo_box.clear()
            self.shot_software_combo_box.addItems(shot_softwares)
            self.shot_software_combo_box.setCurrentText(str(self.entity.engine))

    """
    ========
    Creation
    ========
    """

    def conform_shot(self):
        self.error_text.setText('')
        try:
            self.format_asset_version()
            self.format_shot_version()
            self.format_seq_integer()
            self.format_shot_integer()
            self.format_subtask()
            project = self.input_project_combo_box.currentText()
            sequence = self.input_sequence_combo_box.currentText()
            shot = self.input_shot_combo_box.currentText()
            task = self.input_shot_task_combo_box.currentText()
            subtask = self.input_shot_subtask_combo_box.currentText()
            software = self.shot_software_combo_box.currentText()
            version = self.shot_version.text()
            error, errors = self.check_shot_input()
            if error:
                raise PipeException(str(errors) + ' is missing !')
            # Formatting
            if subtask == '':
                subtask = 'main'
            task = task.split('_')[1]
            if shot != "master":
                shot = "p" + shot
            ext = self.entity.engine.get_file_path().split(".")[-1] or conf.ext_by_soft[self.entity.get_engine()][0]

            subtask = str(subtask).replace(' ', '_').lower()
            project_sid = fs_conf.path_mapping['project'][project]
            new_sid = Sid(data={'project': project_sid, 'seq': 's' + sequence, 'shot': shot,
                                'task': task, 'subtask': subtask, 'version': 'v' + version,
                                'state': 'w', 'ext': ext})

            success = self.entity.conform_entity(new_sid)
            if success:
                self.success(success)

        except PipeException as pe:
            self.error_text.setText(str(pe))

    def conform_asset(self):
        self.error_text.setText('')
        try:
            self.format_seq_integer()
            self.format_shot_integer()
            self.format_name()
            project = self.input_project_combo_box.currentText()
            cat = self.asset_type_combo_box.currentText()
            name = self.input_asset_name_combo_box.currentText()
            task = self.input_asset_task_combo_box.currentText()
            subtask = self.input_asset_subtask_combo_box.currentText()
            version = self.asset_version.text()
            error, errors = self.check_asset_input()
            if error:
                raise PipeException(str(errors) + ' is missing !')
            project_sid = fs_conf.path_mapping['project'][project]
            ext = self.entity.engine.get_file_path().split(".")[-1] or conf.ext_by_soft[self.entity.get_engine()][0]
            # TODO Create the entity object to pass

            print("NAME : " + str(name))

            new_sid = Sid(data={'project': project_sid, 'cat': cat, 'name': name,
                                'task': task, 'subtask': subtask, 'version': 'v' + version,
                                'state': 'w', 'ext': ext})

            success = self.entity.conform_entity(new_sid)
            if success:
                self.success(success)

        except PipeException as pe:
            self.error_text.setText(str(pe))

    def check_shot_input(self):
        """
        check if errors
        :return: the error to display
        """
        error = False
        errors = []
        # sequence
        if self.input_sequence_combo_box.currentText() == '':
            errors.append('Sequence')
            error = True
        # shot
        if self.input_shot_combo_box.currentText() == '':
            errors.append('Shot')
            error = True
        # task
        if self.input_shot_task_combo_box.currentIndex() == 0:
            errors.append('Task')
            error = True
        # subtask
        if self.input_shot_subtask_combo_box.currentText() == '':
            subtask = 'main'
        # version
        if self.shot_software_combo_box.currentText() not in conf.softwares:
            errors.append('Software')
            error = True
        if self.shot_version.text() == '':
            errors.append('Version')
            error = True

        return error, errors

    def check_asset_input(self):
        """
        check if errors
        :return: the error to display
        """
        error = False
        errors = []
        # cat
        if self.asset_type_combo_box.currentText() == "":
            errors.append('Category')
            error = True
        # asset
        if self.input_asset_name_combo_box.currentText() == '':
            errors.append('Name')
            error = True
        # task
        if self.input_asset_task_combo_box.currentIndex() == 0:
            errors.append('Task')
            error = True
        # subtask
        if self.input_asset_subtask_combo_box.currentText() == '-- Select a subtask --' or self.input_asset_subtask_combo_box.currentText() == '':
            errors.append('Subtask')
            error = True

        return error, errors

    """
    =================
    Gestion User Conf
    =================
    """

    def save_user_conf(self):
        project = self.input_project_combo_box.currentText()
        conf.set('project', project)
        print 'user config updated : '+project+' is now the default project'

    def read_user_conf(self):
        # print 'user conf : ',uc.read_user_conf()
        index = self.input_project_combo_box.findText(conf.project) or 0
        self.input_project_combo_box.setCurrentIndex(index)

    """
    ========================
    Open Created File Pop Up
    ========================
    """
    
    def success(self, sid):
        if self.shot_software_combo_box.currentText() == str(self.entity.engine):
            msg = QMessageBox()
            msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            msg.setIcon(QMessageBox.Information)
            msg.setText("You file as been created")
            msg.setInformativeText("You work actually on the pipeline file")
            msg.setWindowTitle("Success")
            msg.show()
            msg.exec_()
            # self.entity.engine.save(sid.path) => do in the entity

        if self.main_windows:
            self.main_windows.sid = sid
            self.main_windows.update_view()


if __name__ == '__main__':

    import sys
    from Qt import QtGui

    app = QtWidgets.QApplication(sys.argv)
    fm = ConformWindow()
    fm.setPalette(QtGui.QPalette())
    fm.show()
    app.exec_()
