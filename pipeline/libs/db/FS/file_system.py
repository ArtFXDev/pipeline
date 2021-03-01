import os
import sys
import stat
import shutil
import math  # For convert size
import time
import json
import subprocess
from datetime import datetime  # For format date
from pathlib2 import Path
# Pipeline
from pipeline import conf
from pipeline.libs.utils import pipe_exception as pe
from pipeline.libs.utils import log
from spil.libs.fs.fs import FS
from spil.conf import fs_conf


class FileSystem(object):
    """
    File system class
    Manage the system uses
    """

    def __init__(self):
        pass

    # region Workspace
    """
    ===================
    Workspace Creations
    ===================
    """

    def create_shot_3d_workspace(self, sid):
        """
        Create the workspace for the 3d shot folder
        """
        print "create_shot_3d_workspace : conf.root = "+conf.root
        for key, value in fs_conf.path_mapping['project'].items():
            if value == sid.project:
                project = key
        workspace_template = self.workspace_init(
            conf.workspace_template.format(project=project))
        print "workspace_template = "+workspace_template
        shot_workspace_path = conf.shot_workspace_path.format(
            project=project, dimension='3d')
        print "shot_workspace_path = "+shot_workspace_path
        self.workspace_mel_init(
            workspace_template, shot_workspace_path + '/workspace.mel')
        self.create_folders(shot_workspace_path, conf.folder_workspace)

    def create_shot_2d_workspace(self, sid):
        """
        Create the workspace for the 2d shot folder
        """
        project = sid.get('project')
        # TODO  in sid
        project = ""
        for key, value in fs_conf.path_mapping['project'].items():
            if value == sid.get('project'):
                project = key
        # TODO end
        shot_workspace_path = conf.shot_workspace_path.format(
            project=project, dimension='2d')
        self.create_folders(shot_workspace_path, conf.folder_workspace)

    def create_asset_workspace(self, sid):
        """
        Create the workspace for the asset folder
        """
        project = sid.get('project')
        for key, value in fs_conf.path_mapping['project'].items():
            if value == sid.project:
                project = key
        workspace_template = self.workspace_init(
            conf.workspace_template.format(project=project))
        asset_workspace_path = conf.asset_workspace_path.format(
            project=project, cat=sid.cat, name=sid.name)
        self.workspace_mel_init(
            workspace_template, asset_workspace_path + '/workspace.mel')
        self.create_folders(asset_workspace_path, conf.folder_workspace)

    def workspace_init(self, workspace_path):
        """
        Test if the workspace exist
        :return: the default workspace
        """
        if not os.path.exists(workspace_path):
            log.debug('Cannot find templates, switching to default')
            return conf.default_workspace_template

    def workspace_mel_init(self, workspace_path, workspace_path_mel):
        """
        Test if the workspace exist if not copy .mel
        """
        if not os.path.exists(workspace_path_mel):
            log.debug('Workspace.mel copied')
            shutil.copy(workspace_path, workspace_path_mel)

    # endregion

    # region Template
    """
    ===================
    Template Creations
    ===================
    """

    def template_init(self, path_template, file_name, engine):
        """
        Init the template
        :return: The template path
        """
        if not os.path.exists(path_template):
            path_template = conf.default_scene_templates.format(
                software=engine)
        return os.path.join(path_template, file_name)

    # endregion

    # region Create Entity
    """
    ===================
      File Creations
    ===================
    """

    def create_shot(self, sid, tag='', comment=''):
        """
        Create a shot
        :param sid: Sid fill with datas
        :return The path where is create
        """
        if sid.is_asset():
            raise pe.PipeException('Sid need to be a shot for create a shot')
        if not sid.has_a('ext'):
            raise pe.PipeException(
                'Sid need to be fill with a extension. Sid: ' + str(sid))

        engine_crate = conf.get_soft_by_ext(sid.ext)

        # file path
        path = sid.get_as('state').path

        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise pe.PipeException("File already exist")
        """
        Template
        """
        path_template = conf.scene_templates.format(
            project=sid.project, software=engine_crate)
        file_name_template = conf.shot_template_name.format(
            software=engine_crate, ext=sid.ext)

        path_template = self.template_init(
            path_template, file_name_template, engine_crate)

        shutil.copy(path_template, sid.path)

        # COMMENT FILE TODO Maybe in the conf (txt file base)
        if comment == '':
            comment = "Created on {d} at {h} \n\n".format(d=time.strftime('%A %d/%m/%Y'), h=time.strftime(
                '%H:%M')) + 'Sequence : {sequence}\n' \
                            'Shot : {shot}\n' \
                            'Task : {task}\n' \
                            'Subtask : {subtask}\n'.format(
                sequence=sid.seq, shot=sid.shot, task=sid.task, subtask=sid.subtask)

        # TODO PASS A FILE OBJECT
        self.create_package_file(sid.get_as('state'), comment, tag)

        # CREATE WORKSPACE
        if sid.task == 'comp':
            self.create_shot_2d_workspace(sid)
        else:
            self.create_shot_3d_workspace(sid)
        return sid

    def create_asset(self, sid, tag='', comment=''):
        """
        Create a shot
        :param sid: Sid fill with datas
        :return The path where is create
        """
        if sid.is_shot():
            raise pe.PipeException('Sid need to be a asset for create a asset')
        if not sid.has_a('ext'):
            raise pe.PipeException(
                'Sid need to be fill with a extension. Sid: ' + str(sid))

        engine_crate = conf.get_soft_by_ext(sid.ext)

        # file path
        # error here : reformat the file path with the task name as 'numTask_taskName' like '03_modeling'.
        # question does it should be fixed here ? in the entity class or in the sid.path() function ?

        path = sid.get_as('state').path
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise pe.PipeException('File already exist !')
        """
        Template
        """
        path_template = conf.scene_templates.format(
            project=sid.project, software=engine_crate)
        file_name_template = conf.asset_template_name.format(
            subtask=engine_crate, ext=sid.ext)

        path_template = self.template_init(
            path_template, file_name_template, engine_crate)
        shutil.copy(path_template, sid.path)

        # COMMENT FILE TODO Maybe in the conf (txt file base)
        if comment == '':
            comment = "Created on {d} at {h} \n\n".format(d=time.strftime('%A %d/%m/%Y'), h=time.strftime(
                '%H:%M')) + 'Category : {cat}\n' \
                            'Name : {name}\n' \
                            'Task : {task}\n' \
                            'Subtask : {subtask}\n'.format(
                cat=sid.cat, name=sid.name, task=sid.task, subtask=sid.subtask)

        self.create_package_file(sid.get_as('state'), comment, tag)

        # CREATE WORKSPACE
        self.create_asset_workspace(sid)

        return sid

    def make_new_version(self, sid, tag, description):
        """
        This function create a new directory af the max version and return the path
        Create a json with description
        :return The new sid
        """
        new_sid = self.get_next_version(sid)
        if not os.path.exists(new_sid.path):
            os.makedirs(new_sid.path)
        else:
            raise pe.PipeException('File already exist !')
        sid.set('version', new_sid.version)
        if tag != '':
            self.create_tag_file(new_sid, tag)
        self.create_txt_file(new_sid, description)
        return sid

    def create_package_file(self, sid, text, tag=''):
        """
        Create a txt file and the tag file
        """
        self.create_txt_file(sid, text)
        if tag != '':
            self.create_tag_file(sid, tag)

    def create_publish(self, sid, tag='', comment=''):
        """
        Create a publish
        :param sid: Sid fill with datas
        :return The path where is create
        """
        if not sid.has_a('ext'):
            raise pe.PipeException('Sid need to be fill with a extension. Sid: ' + str(sid))
        # file path
        path = sid.get_as('state').path

        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise pe.PipeException('File already exist !')

        # COMMENT FILE TODO Maybe in the conf (txt file base)
        if comment == '':
            comment = "Publish on {d} at {h} \n\n".format(
                d=time.strftime('%A %d/%m/%Y'), h=time.strftime('%H:%M'))

        self.create_package_file(sid.get_as('state'), comment, tag)

        return sid

    def create_publish_valid(self, sid_publish):
        """
        Create the publish valid (actualy a copy of the last publish)
        :return: sid to save
        """
        sid_publish_valid = sid_publish.copy()

        sid_publish_valid.set('version', 'valid')
        path = sid_publish_valid.get_as('state').path
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        path = Path(path) / (sid_publish.version + '.version')
        path.write_text(unicode())
        return sid_publish_valid

    # endregion

    # region Getter
    """
    ================
        Getter
    ================
    """

    def get(self, sid):
        """
        Return the list of folder in the sid with glob
        :return List of folder in the sid
        """
        return FS.get(sid)

    def get_files(self, sid):
        """
        Return the list of file in the sid
        :return List of file in the sid
        """
        files = []
        if sid.has_a('ext'):
            sid = sid.get_as('state')
        path = sid.path
        if os.path.exists(path):
            for f in os.listdir(path):
                files.append(f)
        return files

    def get_dirs(self, path):
        """
        Return the list of directory in the path
        :return List of directory in the path
        """
        dirs = []
        if os.path.exists(path):
            for f in os.listdir(path):
                dirs.append(f)
        return dirs

    def get_extension(self, sid):
        """
        Get the extension inside the folder (sid)
        :return The extension of the soft file (ex: ma or hipnc)
        """
        sid = sid.get_as('state')
        ext = ''
        for f in self.get_files(sid):
            ext_loop = os.path.splitext(f)[1].replace('.', '')
            if ext_loop in conf.extensions:
                ext = ext_loop
        return ext

    def get_tag(self, sid):
        """
        Get the tag inside the folder (sid)
        :return The tag for the sid pass in parameter
        """
        tag = ''
        for f in self.get_files(sid):
            if os.path.splitext(f)[1] == '.tag':
                tag = os.path.splitext(f)[0]
        return tag

    def get_date(self, sid):
        """
        Get the date inside the folder (sid)
        :return The date for the sid pass in parameter
        """
        date = '00/00/0000 00:00'
        path = sid.get_as('state').path
        for f in self.get_files(sid):
            if os.path.splitext(f)[1].replace('.', '') in conf.extensions:
                time_span = os.path.getctime(os.path.join(path, f))
                date = '  ' + \
                    str(datetime.fromtimestamp(time_span).strftime(
                        '%d/%m/%Y %H:%M')) + '  '
        return date

    def get_size(self, sid):
        """
        Get the size of the file (ex: 50Mo)
        :return: The size of the file (ex: 50Mo)
        """
        size = 0
        path = sid.get_as('state').path
        for f in self.get_files(sid):
            if os.path.splitext(f)[1].replace('.', '') in conf.extensions:
                size = self.convert_size(
                    os.path.getsize(os.path.join(path, f)))
        return size

    def get_next_version(self, sid):
        """
        Get the next version existing
        :return The number of the next version (last + 1)
        """
        if sid.has_a('version'):
            sid_result = sid.copy()
            max_version = 0
            path = sid_result.get_as('subtask').path
            if os.path.exists(path):
                for f in os.listdir(path):
                    if len(f.split('_')) == 2:
                        version_folder = f.split('_')[1][1:]
                        if os.path.isdir(os.path.join(path, f)) and version_folder.isdigit():
                            version_folder = int(version_folder)
                            if max_version < version_folder:
                                max_version = version_folder
            max_version = 'v' + str(int(max_version) + 1).zfill(3)
            sid_result.version = max_version
            return sid_result.get_as('state')
        else:
            log.info('Sid not valid, version is missing !')
    # endregion

    # region Utils
    """
    ================
    Function Utils
    ================
    """

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def move_time(self, source, target):
        """
        Move folder source in target folder (or file)
        """
        if os.path.exists(source):
            date_time = str(datetime.now()).replace(':', '_')
            folder = target + '/' + date_time
            # os.mkdir(folder)
            shutil.move(source, folder)

    def move(self, source, target):
        """
        Move folder source in target folder (or file)
        """
        shutil.move(source, target)

    # endregion

    # region Create File
    """
    ================
      File creation
    ================
    """

    def create_txt_file(self, sid, value):
        """
        Create a txt file in the sid path with the value written in
        """
        if sid.has_a('version'):
            path = Path(sid.path) / 'comment.txt'
            path.write_text(unicode(value))
        else:
            raise pe.PipeException('Sid not valid, version is missing !')

    def create_tag_file(self, sid, tag):
        """
        Create a .tag file in the sid path with the value written in
        """
        if sid.has_a('version'):
            tag_name = tag.replace(' ', '_') + '.tag'
            path = Path(sid.path) / tag_name
            path.write_text(unicode())
        else:
            raise pe.PipeException('Sid not valid, version is missing !')

    def create_folder(self, path, folder_name):
        """
        Create the folder in the path
        """
        try:
            Path(path + '/' + folder_name).mkdir(parents=True, exist_ok=True)
        except Exception as ex:
            raise pe.PipeException(ex.message)

    def create_path(self, path):
        """
        Create the folder in the path
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except Exception as ex:
            raise pe.PipeException(ex.message)

    def create_folders(self, path, folders):
        """
        Create all the folders list in the path, recursiv function
        """
        if not isinstance(folders, list):
            raise pe.PipeException(
                'Create folders need a list of folders and not a {}'.format(type(folders).__name__))
        for folder in folders:
            self.create_folder(path, folder)

    def get_data_json(self, path):
        """
        Get the data inside json file
        :return: the data
        """
        with open(path) as load_file:
            data = json.load(load_file)
        return data

    def write_data_json(self, path, data):
        """
        Update the json with new datas
        """
        with open(path, 'w') as write_file:
            json.dump(data, write_file)

    # endregion

    # region Conforming
    """
    ===============
    File Conforming
    ===============
    """

    def conform_shot(self, sid):
        """
        Conform a existing file into the pipe nomenclature don't save the file
        :return: The path to save
        """
        if sid.is_asset():
            raise pe.PipeException('Sid need to be shot type for conform shot')
        if not sid.has_a('ext'):
            raise pe.PipeException(
                'Sid need to be fill with a extension. Sid: ' + str(sid))

        engine_conform = conf.get_soft_by_ext(sid.ext)
        # file creation
        path = sid.get_as('state').path

        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise pe.PipeException('File already exist !')

        # COMMENT FILE
        value = "Conformed " + "on {d} at {h} \n\n".format(d=time.strftime('%A %d/%m/%Y'), h=time.strftime(
            '%H:%M')) + 'Sequence : {sequence}\n' \
                        'Shot : {shot}\n' \
                        'Task : {task}\n' \
                        'Subtask : {subtask}\n' \
                        'Software : {software}\n' \
                        'Version : {version}\n\n'.format(
            sequence=sid.seq, shot=sid.shot, task=sid.task,
            subtask=sid.subtask, software=engine_conform, version=sid.version)

        self.create_package_file(sid.get_as('state'), value)

        # CREATE WORKSPACE
        if sid.task == 'comp':
            self.create_shot_2d_workspace(sid)
        else:
            self.create_shot_3d_workspace(sid)

        return sid

    def conform_asset(self, sid):
        """
        Conform a existing file into the pipe nomenclature
        :return: The path where the file is conform
        """
        if sid.is_shot():
            raise pe.PipeException(
                'Sid need to be asset type for conform asset')
        if not sid.has_a('ext'):
            raise pe.PipeException(
                'Sid need to be fill with a extension. Sid: ' + str(sid))

        # file creation
        path = sid.get_as('state').path

        if not os.path.exists(path):
            os.makedirs(path)
        else:
            raise pe.PipeException('File already exist !')

        # COMMENT FILE
        value = "Conformed on {d} at {h} \n\n".format(d=time.strftime('%A %d/%m/%Y'), h=time.strftime(
                '%H:%M')) + 'Category : {cat}\n' \
                            'Name : {name}\n' \
                            'Task : {task}\n' \
                            'Subtask : {subtask}\n' \
                            'Version : {version}\n\n'.format(
            cat=sid.cat, name=sid.name, task=sid.task, subtask=sid.subtask, version=sid.version)

        self.create_package_file(sid.get_as('state'), value)

        # CREATE WORKSPACE
        self.create_asset_workspace(sid)

        return sid

    # endregion


if __name__ == '__main__':

    from spil.libs.sid import Sid
    sid_test = Sid(
        path="I:/SynologyDrive/ARAL/03_WORK_PIPE/01_ASSET_3D/01_characters/dummy/3d/scenes/01_modeling/maya/work_v001")
    # Get
    print('SID : ' + str(sid_test))
    print('get_files : ' + str(FileSystem.get_files(sid_test)))
    print('get_extension : ' + FileSystem.get_extension(sid_test))
    print('get_tag : ' + FileSystem.get_tag(sid_test))
    print('get_date : ' + FileSystem.get_date(sid_test))
    print('get_size : ' + FileSystem.get_size(sid_test))
    print('get_next_version : ' + str(FileSystem.get_next_version(sid_test)))
    # File create
    FileSystem.create_txt_file(sid_test, "Write test")
    FileSystem.create_tag_file(sid_test, "tag test")

    shotSid = Sid(
        path=r"I:\SynologyDrive\ARAL\03_WORK_PIPE\02_SHOT\3d\scenes\s010\p010\fx\pyro\work_v012\s010_p010.ma")
    assetSid = Sid(
        path=r"I:\SynologyDrive\ARAL\03_WORK_PIPE\01_ASSET_3D\01_characters\dieu\3d\scenes\02_modelinglowres\maya\work_v005\dieu.ma")
    # FileSystem.create_shot(shotSid)
    # FileSystem.create_asset(assetSid)

    sid = FileSystem.make_new_version(sid_test, '', '')
    print 'MAKE NEW VERSION RETOUR . ' + str(sid)
