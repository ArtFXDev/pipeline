import sys
import os
import maya.mel as mel
import maya.cmds as mc

print('Pipeline load Sylvain Work\n')
sys.path.append('W:/pipeline/packages/pipeline')
sys.path.append('W:/pipeline/packages/pipeline/pipeline/libs')
sys.path.insert(0, '//multifct/tools/pipeline/global/packages')
sys.path.append('W:/pipeline/packages/submitter_artfx')

try:
    from pipeline.libs.engine.maya_utils import shelf
    print('Loaded custom shelve')
except Exception as e:
    print('Problem loading Pipeline shelve')
    print(e)

# Prevent close to save

from maya import cmds as mc

pipeline_win = None

def closeCallback():
    from pipeline import conf
    from pipeline.libs.manager.entities import Entities
    entity = Entities()
    actual_sid = entity.get_engine_sid()
    if actual_sid.has_a("ext"):
        conf.set("last_maya_file", mc.file(q=True, sceneName=True))


mc.scriptJob(event=["quitApplication", closeCallback], protected=True)



