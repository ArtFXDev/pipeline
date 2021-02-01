import os
import maya.cmds as cmds

# FIXME : extensions config


# FIXME : this is WIP !!

def init_render(sid, ext='exr'):

    if not sid:
        return

    sid.set(ext='')
    file_name = os.path.splitext(os.path.basename(sid.path))[0]

    rg = cmds.ls(type='renderGlobals')
    if rg:
        rg = rg[0]
    print rg

    config = {
        'outFormatControl': 0,
        'animation': 1,
        'putFrameBeforeExt': 1,
        'extensionPadding': 3,
        'periodInExt': 1,
        'useMayaFileName': 0,
        'imageFormat': 8
    }

    for key, value in config.iteritems():
        cmds.setAttr('{}.{}'.format(rg, key), value)
    cmds.setAttr('{}.{}'.format(rg, 'imageFilePrefix'), 's010_p010', type='string')










