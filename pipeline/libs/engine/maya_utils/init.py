from spil.libs.util import log
from pipeline import conf
from spil.conf import fs_conf
from pipeline.libs.manager.entities import Entities
import maya.mel as mel
import maya.cmds as mc

def init_scene():
    log.info("Initialisation de la scene maya")

    entity = Entities()
    sid = entity.get_engine_sid()
    log.info("Initialisation de la scene maya")
    log.info("file : " + mc.file(query=True, sceneName=True))
    if sid.has_a("ext"):
        log.info("Initialisation des shelfs")
        # Shelf
        project_path = sid.path.split("03_WORK_PIPE")[0]
        shelf_path = project_path + "03_WORK_PIPE/04_TOOLS/01_SHELVES"
        if os.path.exists(shelf_path):
            files = os.listdir(shelf_path)
            for f in files:
                path_file = shelf_path + "/" + f
                if os.path.isfile(path_file):
                    ext = f.split(".")[-1]
                    if ext == "mel":
                        log.info("import file " + f)
                        try:
                            mel_cmd = 'loadNewShelf "' + path_file + '"'
                            mel.eval(mel_cmd)
                        except RuntimeError:
                            log.warn("shelf, not loaded correctly, it's may have been already loaded")
        log.info("Initialisation du workspace")
        # Workspace
        project = ''
        for key, value in fs_conf.path_mapping['project'].items():
            if value == sid.project:
                project = key
        if str(sid).split('/')[1] == 's':
            workspace_path = conf.shot_workspace_path.format(
                root=conf.root, project=project, dimension='3d')
        else:
            workspace_path = conf.asset_workspace_path.format(root=conf.root, project=project,
                                                              cat=sid.cat, name=sid.name)
        entity.engine.set_workspace(workspace_path)
        log.info("workspace set to {}".format(workspace_path))
