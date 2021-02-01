import imp

imp.load_source("pulsar", "C:/Users/julien/Documents/Pipeline/Pulsar/engines/Pulsar_Nuke.py")


def knob_autoWritePath():
    # from pipeline.libs.engine import engine
    # engine = engine.get()
    # sid = engine.get_sid()

    # print 'sid : ', sid
    # sid.set(ext='exr', frame='####')

    # print sid
    # print sid.path

    # writePath = sid.path

    writePath = r'i:/SynologyDrive/DEMO/03_WORK_PIPE/02_SHOT/2d/scenes/s010/p010/comp/main/work_v001/s010_p010.####.jpg'

    print(writePath)

    print writePath.replace('\\', '/')

    myWriteNode = nuke.thisNode()
    print(myWriteNode)

    # for i in range (myWriteNode.getNumKnobs()):
    #    print i
    #    print myWriteNode.knob (i).name()

    myWriteNode.knob(2).setValue(writePath)
    # nuke.execute("Write2",start=1,end=10,incr=2)


print
print knob_autoWritePath

nuke.addOnCreate(lambda: nuke.tprint("OnCreate called for " + nuke.thisNode().name()))

nuke.removeOnCreate(knob_autoWritePath, nodeClass='Write')
nuke.addOnCreate(knob_autoWritePath, nodeClass='Write')

# wNode['Write1'].setValue(writePath)