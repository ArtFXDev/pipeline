import sys
import os

if r'W:\pipeline\packages\pipeline' not in sys.path:

    print 'Pipeline load Sylvain\n'

    sys.path.append(r'W:\pipeline\packages\pipeline')
    sys.path.append(r'W:\pipeline\packages\pipeline\pipeline\libs')
    sys.path.insert(0, '//multifct/tools/pipeline/global/packages')
    sys.path.append(r"W:\pipeline\packages\submitter_artfx")
    # sys.path.append(r"//multifct/tools/pipeline/prod/packages/Tractor-ArtFx/houdini")

from pipeline.libs.engine import houdini_engine
from spil.libs.sid import sid
from spil.libs.util import log

log.setLevel(log.ERROR)

engine = houdini_engine.HoudiniEngine()
try:
    sid = sid.Sid(path=engine.get_file_path())
    engine.set_env_var(sid.path)
except:
    pass

from pipeline.libs.engine.houdini_utils import launch
launch.load_shelves()
