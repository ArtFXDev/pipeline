import os
from engine import Engine
import time
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as mui
from shiboken2 import wrapInstance
from Qt.QtWidgets import QWidget
import warnings
import tempfile
# Sid
from spil.libs.sid import Sid


class MayaEngine(Engine):

    def get_window(self):
        ptr = mui.MQtUtil.mainWindow()
        return wrapInstance(long(ptr), QWidget)

    def open(self, path):
        """
        Open file
        """
        path = self.conform(path)
        cmds.file(path, open=True, force=True)
        cmds.fileInfo("licence", "education")

    def open_as(self, path):  # smell
        """
        Open file and rename it with a time value
        for keep the source file
        """
        path = self.conform(path)
        cmds.file(path, open=True, force=True)
        cmds.file(rename=path.replace(
            ".ma", "_{}.ma".format(time.time())))

    def save(self, path, **kwargs):
        """
        Save file as path
        """
        path = self.conform(path)
        cmds.file(rename=path)
        ext_file = os.path.splitext(path)[1]
        if ext_file == '.ma':
            cmds.file(save=True, type="mayaAscii", **kwargs)
        elif ext_file == '.mb':
            cmds.file(save=True, type="mayaBinary", **kwargs)

    def get_namespace(self, sid):
        """
        Get the namespace of the given sid
        :param sid sid: Sid to get namespace
        :return str: The namespace
        """
        task_name = sid.get("task")
        task_name = task_name.split("_")[-1]
        if sid.is_shot():
            return "{0}_{1}_{2}".format(sid.get("seq"), sid.get("shot"), task_name)
        else:
            return "{0}_{1}".format(sid.get("name"), task_name)

    def create_reference(self, sid_ref, have_namespace=False, forced_namespace=None):
        """
            create a reference to the scene defined by sid_ref on the current scene.
        """
        import pymel.core as pm
        if not have_namespace:
            pm.createReference(sid_ref.path)
            return 0
        if not forced_namespace:
            forced_namespace = self.get_namespace(sid_ref)
        namespace_list = pm.listNamespaces()  # get the namespace list of all references
        counter = self.make_counter(forced_namespace, namespace_list)  # return a formatted counter
        forced_namespace += "__" + counter
        # create the reference
        pm.createReference(sid_ref.path, namespace=forced_namespace)
        # cmds.file(sid_ref.path, r=True, ignoreVersion = True, namespace = file_namespace )

    def make_counter(self, file_namespace, ref_list):
        """
            count the number of file containing namespace in their name and return a counter formatted as '001,002...010,011'
        """
        count = 1.0  # define it as float
        # count how many words contain the 'file_namespace' word in their name
        for namespace in ref_list:
            if file_namespace in namespace:
                count += 1
        # format the counter to get something like 011,013
        count = count / 100  # get number as 0.01,0.02...
        f_counter = "{0:.2f}".format(count)  # get the counter as '0.10'
        f_counter = f_counter.replace(".", "")  # remove the '.' to get '010'
        return f_counter

    def get_sid(self):
        """
        Get the sid of the current file
        """
        path = self.get_file_path()
        cur_sid = Sid(path=path)
        return cur_sid

    def is_batch(self):
        return cmds.about(batch=True)

    def create_tmp_file(self, sid):
        """
        Create a tmp file to do stuff freely
        :param sid: sid to save as tmp
        :return str: tmp path to maya scene
        """
        self.save(sid.path)
        tmp_sid = sid.copy()
        tmp_dir = tempfile.gettempdir()
        path_dir = os.path.dirname(self.conform(sid.path))
        path = tmp_sid.path.replace(path_dir, os.path.join(tmp_dir, "artfx"))  # Change to tmp directory
        path = path.replace(".{}".format(tmp_sid.get("ext")), "_{}.{}".format(time.time(), tmp_sid.get("ext")))  # add time-span
        cmds.file(path, save=True, writable=False)
        self.open(sid.path)
        return path

    def publish(self):
        """"
        Publish tool
        """
        import pymel.core as pm
        self.import_reference_delete_namespace()
        self.remove_to_delete_set()

    def get_file_path(self):
        """
        Get the current file path (from the current open file)
        """
        return cmds.file(query=True, sceneName=True)

    def set_workspace(self, path):
        """
        Set the workspace
        """
        path = self.conform(path)
        mel.eval('setProject \"' + path + '\"')

    def pre_publish(self):
        """
        Prepare the scene for publish
        """
        self.import_reference_delete_namespace()
        try:
            self.remove_to_delete_set()
        except:
            print('TO_DELETE not exist')

    def import_reference_delete_namespace(self):
        import pymel.core as pm
        for r in pm.listReferences():
            print("Namespace to import/delete : {}".format(r.fullNamespace))
            try:
                pm.FileReference(namespace=r.fullNamespace).importContents(removeNamespace=True)
            except Exeption:
                r.importContents()
        print('References imported\nNamespace deleted')

    def remove_to_delete_set(self):
        import pymel.core as pm
        if not cmds.objExists('TO_DELETE'):
            print('TO_DELETE not exist')
            return
        oset = pm.PyNode('TO_DELETE')
        if oset:
            oset_element = []
            for f in oset:
                oset_element.append(f)
            for f in oset_element:
                pm.delete(f)
            print('TO_DELETE set removed')

    def __str__(self):
        """
        Return the soft name
        """
        return 'maya'


if __name__ == '__main__':
    """
    Test
    """
    # Create engine
    maya = MayaEngine()
    print("Engine : " + str(maya))
    # Get engine path
    print("Current file location : " + maya.get_file_path())
    # Save
    maya.save(r"C:\Users\Sylvain\Desktop\test.ma")
    print("Current file location after save : " + maya.get_file_path())
    # Open as
    maya.open_as(maya.get_file_path())
    print("Open as ")
    print("Current file location after open as : " + maya.get_file_path())
    # Open
    maya.open(r"C:\Users\Sylvain\Desktop\test.ma")
    print("Current file location after open : " + maya.get_file_path())
