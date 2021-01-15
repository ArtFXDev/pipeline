from pipeline import conf
from pipeline.libs.manager.entities import Entities
import hou
entity = Entities()
actual_sid = entity.get_engine_sid()
if actual_sid.has_a("ext"):
    conf.set("last_hou_file", hou.hipFile.path())
