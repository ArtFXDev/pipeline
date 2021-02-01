import os
from Qt.QtWidgets import QMessageBox

root = os.getenv('ROOT_PIPE') or False
# if not root:
#     erreurEnvMsg = QMessageBox()
#     erreurEnvMsg.setIcon(QMessageBox.Critical)
#     erreurEnvMsg.setText('ROOT_PIPE env not exist please setup')
#     erreurEnvMsg.setDetailedText("")
#     erreurEnvMsg.exec_()
