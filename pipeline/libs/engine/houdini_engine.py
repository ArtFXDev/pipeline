from engine import Engine
import os
import hou
import time
from spil.libs.sid.sid import Sid


class HoudiniEngine(Engine):

    def get_window(self):
        return hou.qt.mainWindow()

    def open(self, path):
        """
        Open file
        """
        hou.hipFile.load(path, suppress_save_prompt=True)
        self.set_env_var(path)

    def set_env_var(self, path):
        """
        Workspace
        """
        workspace_path = path.split('/scenes')[0]
        pnum = ''
        snum = ''
        name = ''
        if '02_SHOT' in path.split('/'):
            shot_path = path.split('02_SHOT')[0] + '02_SHOT/3d'
            asset_path = path.split('02_SHOT')[0] + '01_ASSET_3D'
            pnum = path.split('/')[8]
            snum = path.split('/')[7]
            wipcache_path = os.path.join(path.split('02_SHOT/3d/scenes')[0],
                                         '03_WIP_CACHE_FX', pnum, snum).replace(os.sep, '/')
            pubcache_path = os.path.join(path.split('02_SHOT/3d/scenes')[0],
                                         '04_PUBLISH_CACHE_FX', pnum, snum).replace(os.sep, '/')
        else:
            shot_path = path.split('01_ASSET_3D')[0] + '02_SHOT/3d'
            asset_path = path.split('01_ASSET_3D')[0] + '01_ASSET_3D'
            name = path.split('/')[6]
            wipcache_path = os.path.join(path.split('01_ASSET_3D')[
                                         0], '03_WIP_CACHE_FX', name).replace(os.sep, '/')
            pubcache_path = os.path.join(path.split('01_ASSET_3D')[
                                         0], '04_PUBLISH_CACHE_FX', name).replace(os.sep, '/')

        sid = Sid(path=path)
        if sid.is_shot():
            farm = sid.get('project').upper() + '_' + \
                sid.get('seq') + '_' + sid.get('shot')
        elif sid.is_asset():
            farm = sid.get('project').upper() + '_' + sid.get('name')
        project = path.split('/03_WORK_PIPE')[0]

        hou.putenv('JOB', workspace_path)
        hou.putenv('WIPCACHE', wipcache_path)
        hou.putenv('PUBCACHE', pubcache_path)
        hou.putenv('ASSET', asset_path)
        hou.putenv('SHOT', shot_path)
        hou.putenv('PNUM', pnum)
        hou.putenv('SNUM', snum)
        hou.putenv('ASSET_NAME', name)
        hou.putenv('FARM', farm)
        hou.putenv('PROJECT', project)

        print("JOB : {}".format(workspace_path))
        print("WIPCACHE : {}".format(wipcache_path))
        print("PUBCACHE : {}".format(pubcache_path))
        print("ASSET : {}".format(asset_path))
        print("SHOT : {}".format(shot_path))
        print("PNUM : {}".format(pnum))
        print("SNUM : {}".format(snum))
        print("ASSET_NAME : {}".format(name))
        print("FARM : {}".format(farm))
        print("PROJECT : {}".format(project))

    def open_as(self, path):
        """
        Open file and rename it with a time value
        for keep the source file
        """
        path = self.conform(path)
        hou.hipFile.load(path, suppress_save_prompt=True)
        hou.hipFile.setName(path.replace(
            ".hipnc", "_{}.hipnc".format(time.time())))

    def save(self, path):
        """
        Save file as path
        """
        path = self.conform(path)
        hou.hipFile.save(path)

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
        hou.hipFile.save(path)
        self.open(sid.path)
        return path

    def get_file_path(self):
        """
        Get the current file path (from the current open file)
        """
        return hou.hipFile.path()

    def set_workspace(self, path):
        """
        Set the workspace
        """
        path = self.conform(path)
        os.environ["JOB"] = path
        hou.allowEnvironmentToOverwriteVariable("JOB", True)

    def is_batch(self):
        return not hou.isUIAvailable()

    def get_render_nodes(self):
        """
        Get all the output render node that can be submit with the farm
        including merge node and children recursively
        :return dict: dict key: node path value: node type or other dict for merge rop
        """
        output = {}
        hou_render_types = [
            "ifd",
            "arnold",
            "vray_renderer",
            "Redshift_ROP"
        ]

        def get_merge_input(merge_node, parent=None):
            parent = parent or []
            out = {}
            for input in merge_node.inputs():
                if input.type().name() == "merge" and input.path() not in parent:
                    parent.append(merge_node.path())
                    out[input.path()] = get_merge_input(input, parent)
                if input.type().name() not in hou_render_types:
                    continue
                out[input.path()] = input.type().name()
            return out

        def get_merge_output(merge_node, parent=None):
            for output_node in merge_node.outputs():
                if output_node.type().name() == "merge" and output_node.path() not in output.keys():
                    output[output_node.path()] = get_merge_input(output_node, parent)
                    get_merge_output(output_node)

        for render_types in hou_render_types:
            node_type = hou.nodeType(hou.nodeTypeCategories()['Driver'], render_types)
            if not node_type:
                continue
            for _node in node_type.instances():
                output[_node.path()] = _node.type().name()
                for output_node in _node.outputs():
                    if output_node.type().name() != "merge":
                        continue
                    if output_node in output.keys():
                        continue
                    output[output_node.path()] = get_merge_input(output_node)
                    get_merge_output(output_node)

        return output

    def __str__(self):
        return 'houdini'


if __name__ == '__main__':
    """
    Test
    """
    # Create engine
    engine = HoudiniEngine()
    print("Engine : " + str(engine))
    # Get engine path
    print("Current file location : " + engine.get_file_path())
    # Save
    engine.save(r"C:\Users\Sylvain\Desktop\test" + engine.get_ext())
    print("Current file location after save : " + engine.get_file_path())
    # Open as
    engine.open_as(engine.get_file_path())
    print("Open as ")
    print("Current file location after open as : " + engine.get_file_path())
    engine.save(engine.get_file_path())
    # Open
    engine.open(r"C:\Users\Sylvain\Desktop\test" + engine.get_ext())
    print("Current file location after open : " + engine.get_file_path())
