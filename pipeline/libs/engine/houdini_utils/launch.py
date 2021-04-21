import hou
import os

here = os.path.dirname(__file__)

# todo : there is a problem when the pipeline shelf is loading on a houdini session with a shelf that already named "pipeline". Fix iiiit

def load_shelves():
    # print "Here : ", here
    shelf_dir = os.path.join(here, 'shelves')
    try:
        from pathlib2 import Path
        print("loading shelves")
        for shelf_path in Path(shelf_dir).iterdir():
            shelf_path = str(shelf_path).replace(os.sep, r'/')
            # print shelf_path
            shelf_name = os.path.basename(shelf_path).split('.')[0]
            #print("installing " + shelf_name)
            newShelf = False
            #print("shelf_path = " + shelf_path)
            local_shelf = hou.shelves.defaultFilePath()
            #print("local_shelf = " + local_shelf)
            if os.path.exists(local_shelf):
                hou.shelves.loadFile(local_shelf)
                #print("local shelf loaded")

            #print("shelfSets = " + str(hou.shelves.shelfSets()))
            #print("shelves = " + str(hou.shelves.shelves()))

            if shelf_name not in hou.shelves.shelfSets():
                hou.shelves.loadFile(shelf_path)
                # if shelf_name
                newShelf = True
                #print('Loaded shelf : {}'.format(shelf_name))
                #print("Home = " + str(hou.homeHoudiniDirectory()))
            else:
                print("shelves already exist")

                '''
                if the tool already exist :
                    replace
                 else :
                    add it to the shelf
                '''

    except Exception as e:
        print('Problem loading Pipeline shelves')
        print(e)

def load_pipeline_shelves():
    shelf_dir = os.path.join(here, 'shelves')
    try:
        from pathlib2 import Path
        print("loading shelves")
        for shelf_path in Path(shelf_dir).iterdir():
            shelf_path = str(shelf_path).replace(os.sep, r'/')
            shelf_name = os.path.basename(shelf_path).split('.')[0]
            local_shelf = hou.shelves.defaultFilePath()
            if os.path.exists(local_shelf):
                hou.shelves.loadFile(local_shelf)
            if shelf_name not in hou.shelves.shelfSets():
                hou.shelves.loadFile(shelf_path)
            else:
                print("shelves already exist")
    except Exception as e:
        print('Problem loading Pipeline shelves')
        print(e)

def load_custom_shelves(path):
    shelf_dir = path
    try:
        from pathlib2 import Path
        print("loading shelves")
        for shelf_path in Path(shelf_dir).iterdir():
            shelf_path = str(shelf_path).replace(os.sep, r'/')
            shelf_name, shelf_ext = os.path.basename(shelf_path).split('.')
            if shelf_ext != "hdanc" and shelf_ext != "shelf":
                continue
            local_shelf = hou.shelves.defaultFilePath()
            if os.path.exists(local_shelf):
                hou.shelves.loadFile(local_shelf)
            if shelf_name not in hou.shelves.shelfSets():
                hou.shelves.loadFile(shelf_path)
            else:
                print("shelves already exist")
    except Exception as e:
        print('Problem loading Pipeline shelves')
        print(e)

# load all the hda placed in 03_HDAs
def load_HDAs(hda_lib_path):
    if os.path.exists(hda_lib_path):
        print("Looking HDA here : " + hda_lib_path)
        for i in os.listdir(hda_lib_path):
            split = i.split(".")
            if len(split) > 1 and split[-1] == "hdanc":
                hda_path = hda_lib_path + "/" + i
                hou.hda.installFile(hda_path, change_oplibraries_file=False, force_use_assets=False)
                hou.hda.reloadFile(hda_path)
                if os.getenv("TRACTOR_RUN"):  # Unlock HDA if TRACTOR_RUN env
                    try:
                        for definition in hou.hda.definitionsInFile(hda_path):
                            node_type = definition.nodeType()
                            for node in node_type.instances():
                                node.allowEditingOfContents(propagate=True)
                                print("unlock : {}".format(node))
                    except Exception as ex:
                        print(ex)
    else:
        print("HDA path " + hda_lib_path + " doesn't exist")
