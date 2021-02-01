import sys
import os
# Add pipline path to the system path
pip_path = os.path.dirname(os.path.realpath(__file__))

if pip_path not in sys.path:
    sys.path.append(pip_path)

from tools.filemanager.ui import file_manager as fm_win

reload(fm_win)
reload(fs)

# Open In / Out Widget (FileManager)

file_manager = fm_win.FileManager()
file_manager.show()
