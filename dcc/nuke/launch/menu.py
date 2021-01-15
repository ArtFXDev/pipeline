menubar = nuke.menu("Nuke")
m = menubar.addMenu("Pipeline")
m.addCommand("Explorer", "from pipeline.libs.utils import clear;clear.do_silent();from pipeline.tools import filemanager as fm;fm.launch()", index=1)
m.addCommand("Create", "from pipeline.libs.utils import clear;clear.do_silent();from pipeline.tools.filemanager.ui import create_UI_window as cw;window = cw.CreateWindow();window.show()", index=2)
m.addCommand("Create", "from pipeline.libs.utils import clear;clear.do_silent();from pipeline.tools.filemanager.ui import conform_UI_window as cw;window = cw.CreateWindow();window.show()", index=3)

f = menubar.addMenu("RenderFarm")
f.addCommand(
    "Render", "import submitter as sub;win = sub.SubmitterNuke();win.show()", index=1)

toolbar = nuke.toolbar("Nodes")
#toolbar.addCommand("RenderFarm", "nuke.createNode('\\multifct\tools\pipeline\beta\packages\Tractor-ArtFx\nuke\plugins\SubmitterTractor')")