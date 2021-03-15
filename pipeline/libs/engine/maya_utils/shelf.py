import maya.cmds as mc
import maya.mel as mel


class _shelf():
    '''A simple class to build shelves in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf".'''

    def __init__(self, name="customShelf", iconPath=""):
        self.name = name

        self.iconPath = iconPath

        self.labelBackground = (0, 0, 0, 0.7)
        self.labelColour = (.9, .9, .9)

        self._cleanOldShelf()
        mc.setParent(self.name)
        self.build()

    def build(self):
        '''This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf.'''
        pass

    def addButon(self, label, icon="commandButton.png", command="", doubleCommand=""):
        '''Adds a shelf button with the specified label, command, double click command and image.'''
        mc.setParent(self.name)
        if icon:
            icon = self.iconPath + icon
        mc.shelfButton(width=37, height=37, image=icon, l=label, command=command, dcc=doubleCommand,
                       imageOverlayLabel=label, olb=self.labelBackground, olc=self.labelColour, annotation="artfx_pipeline_default")

    def addMenuItem(self, parent, label, command="", icon=""):
        '''Adds a shelf button with the specified label, command, double click command and image.'''
        if icon:
            icon = self.iconPath + icon
        return mc.menuItem(p=parent, l=label, c=command, i="")

    def addSubMenu(self, parent, label, icon=None):
        '''Adds a sub menu item with the specified label and icon to the specified parent popup menu.'''
        if icon:
            icon = self.iconPath + icon
        return mc.menuItem(p=parent, l=label, i=icon, subMenu=1)

    def _cleanOldShelf(self):
        '''Checks if the shelf exists and empties it if it does or creates it if it does not.'''
        if mc.shelfLayout(self.name, ex=1):
            if mc.shelfLayout(self.name, q=1, ca=1):
                for each in mc.shelfLayout(self.name, q=1, ca=1):
                    mc.deleteUI(each)
        else:
            mc.shelfLayout(self.name, p="ShelfLayout")


###################################################################################

labels = ["Save", "Publish", "FileManager", "RenderFarm", "Create", "Conform", "Last File"]

save_cmd = """
from pipeline.tools import save
save.save()
"""

publish_cmd = """
from pipeline.tools import save
save.publish()
"""

create_cmd = """
from pipeline.tools.filemanager.ui import create_UI_window as cw_win
create_file_win = cw_win.CreateWindow()
create_file_win.show()
"""

conf_cmd = """
from pipeline.tools.filemanager.ui import conform_UI_window as cow_win
conform_file_win = cow_win.ConformWindow()
conform_file_win.show()
"""

fm_cmd = """from pipeline.libs.utils import clear
clear.do()
from pipeline.tools import filemanager as fm
fm.launch()"""


rdf_cmd = """
from submitter import submitter_maya
from pipeline.libs.manager import entities
submitter_maya.run(entities.Entities().get_engine_sid())
"""

recover_cmd = """
from pipeline import conf
from maya import cmds as mc
mc.file(conf.get("last_maya_file"), open=True, force=True)
"""

class customShelf(_shelf):

    def __init__(self):
        _shelf.__init__(self, name="Pipeline", iconPath="//multifct/tools/pipeline/global/misc/icons/")

    def build(self):
        self.addButon(label="Save", icon="save.png", command=save_cmd)
        self.addButon(label="Publish", icon="publish.png", command=publish_cmd)
        mel.eval("addShelfSeparator()")
        self.addButon(label="FileManager", icon="filemanager.png", command=fm_cmd)
        self.addButon(label="RenderFarm", icon="renderfarm.png", command=rdf_cmd)
        mel.eval("addShelfSeparator()")
        self.addButon(label="Create", icon="create.png", command=create_cmd)
        self.addButon(label="Conform", icon="conform.png", command=conf_cmd)
        mel.eval("addShelfSeparator()")
        self.addButon(label="Last File", icon="return.png", command=recover_cmd)


customShelf()
