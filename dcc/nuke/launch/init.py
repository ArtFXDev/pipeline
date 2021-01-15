import sys
import os

print 'Pipeline load Sylvain\n'

sys.path.append('C:/Users/Souls/Documents/pipeline/packages/pipeline')
sys.path.append(
    'C:/Users/Souls/Documents/pipeline/packages/pipeline/pipeline/libs')
sys.path.insert(0, '//multifct/tools/pipeline/global/packages')
sys.path.append(
    'C:/Users/Souls/Documents/pipeline/packages/Tractor-ArtFx/nuke')
sys.path.append(
    'C:/Users/Souls/Documents/pipeline/packages/submitter')

print 'test'
"""
toolbar = nuke.toolbar("Nodes")

toolbar.addCommand( "Test/Pipeline", "from pipeline.libs.utils import clear;clear.do();from pipeline.tools import filemanager as fm;fm.launch()")
toolbar.addCommand( "Test/Create", "from pipeline.libs.utils import clear;clear.do();from pipeline.tools.filemanager.ui import create_UI_window as cw;window = cw.CreateWindow();window.show()")
"""
