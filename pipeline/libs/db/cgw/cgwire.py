
import json
import gazu

from spil.libs.sid import Sid
from pipeline.libs.utils.singleton import Singleton
from spil.libs.fs.fs import FS
from spil.conf import fs_conf

# TODO : mapping confs or change in cgwire to match pipeline: projects, entity types

from pipeline import conf

project_mapping = {  # TODO put into project_conf
    'project': {            # 3 words : initials, otherwise 6 first letters, lowercased
        'Film TEST': 'demo',
        'ARAL': 'aral',
        'ASCEND': 'ascend',
        'Breach': 'breach',
        'Forgot Your Password': 'fyp',
        'VERLAN': 'verlan',
        'ISSEN SAMA': 'issens',
        'MOON_KEEPER': 'moonke',
        'LONE': 'lone',
        'Chaise': 'timesd',
        'HARU': 'haru',
        'RESURGENCE': 'resurg',
        "L'OREE": 'loree',
        'CLAIR DE LUNE': 'cdl',
    },
}


def get_key_project(project):
    for key, value in project_mapping['project'].items():
        if value == project:
            return key


class CgWire():

    def __init__(self):
        gazu.client.set_host("https://artfx.cg-wire.com/api")
        try:
            gazu.log_in(conf.cgwuser, conf.cgwpassword)  # Create entries cgwuser & cgwpassword in your artfx_pipeline/conf.json
        except:
            pass

    def all_open_projects(self):

        result = []
        for project in gazu.project.all_open_projects():

            project_sid_name = project_mapping['project'].get(project.get('name'))
            sid = Sid(project_sid_name)
            if not sid:
                print('Project {} is not conform - skipped'.format(project_sid_name))
                continue
            sid.conform()
            result.append(sid)

        return sorted(result)

    def all_assets_for_project(self, project_name):
        project_name = fs_conf.path_mapping["project"][project_name]
        sid = Sid(project_name + '/a')
        sids = []

        project = gazu.project.get_project_by_name(get_key_project(project_name))
        assets = gazu.asset.all_assets_for_project(project)

        for asset in assets:
            asset_sid = sid.copy()
            asset_sid.name = asset.get('name')

            asset_sid.cat = gazu.asset.get_asset_type(asset.get('entity_type_id')).get('name')
            # Fix cat FS / CGW
            for cat_fs in FS.get_children(asset_sid.get_as('project')):
                if str(asset_sid.get('cat')).lower() in cat_fs.get('cat'):
                    asset_sid.set('cat', cat_fs)
            asset_sid.conform()
            sids.append(asset_sid)
        return sorted(sids)

    def all_for_project(self, project_name):
        sids = self.all_assets_for_project(project_name) + self.all_shots_for_project(project_name)
        return sorted(sids)

    def all_shots_for_project(self, project_name):
        project_name = fs_conf.path_mapping["project"][project_name]
        sid = Sid(project_name + '/s')
        sids = []

        project = gazu.project.get_project_by_name(get_key_project(project_name))
        shots = gazu.shot.all_shots_for_project(project)

        for shot in shots:
            shot_sid = sid.copy()
            shot_sid.shot = shot.get('name')
            shot_sid.seq = gazu.shot.get_sequence(shot.get('parent_id')).get('name')
            shot_sid.conform()
            sids.append(shot_sid)

        return sorted(sids)

    def get_all_status(self, sidParam):

        sid = Sid(sidParam)  # handling the incoming sid or string # FIXME Mapping
        #sid = Sid(sid.project + '/s')
        tasksAll = []

        if sid.is_shot():

            print ("Sid : " + sid.shot)
            print (sid.get_as("shot"))
            print ("Project : " + sid.project)

            shotName = sid.shot
            projectNameCGWire = ""

            for key in project_mapping["project"]:
                if (project_mapping["project"].get(key) == sid.project):
                    projectNameCGWire = key

            print("nameCGWire : " + projectNameCGWire)

            #project = gazu.project.get_project_by_name(project_mapping["project"].get(projectNameCGWire))
            project = gazu.project.get_project_by_name(projectNameCGWire)

            #print (project)
            shots = gazu.shot.all_shots_for_project(project)

            for shot in shots:
                # print ('')
                # print ("Get : " + shot.get('name') + " Name : " + shotName)
                # if(shot.get('name') == shotName):
                if(shot.get('name') == "SH01"):
                    shot_sid = sid.copy()
                    shot_sid.shot = shot.get('name')
                    tasksAll = gazu.task.all_tasks_for_shot(shot)
                    # shot_sid.seq = gazu.shot.get_sequence(shot.get('parent_id')).get('name')
                    # shot_sid.conform()
                    # print ("Shot : " + shot_sid.shot + " " + "Seq : " + shot_sid.seq)
                    # sids.append(shot_sid)

            return tasksAll

        elif sid.is_asset():

            print ("Sid : " + sid.task)
            print (sid.get_as("asset"))
            print ("Project : " + sid.project)

            assetName = sid.name
            projectNameCGWire = ""

            for key in project_mapping["project"]:
                if (project_mapping["project"].get(key) == sid.project):
                    projectNameCGWire = key

            print("nameCGWire : " + projectNameCGWire)

            #project = gazu.project.get_project_by_name(project_mapping["project"].get(projectNameCGWire))
            project = gazu.project.get_project_by_name(projectNameCGWire)

            #print (project)
            assets = gazu.asset.all_assets_for_project(project)

            for asset in assets:
                print ('')
                print ("Get : " + asset.get('name'))
                # if(shot.get('name') == assetName):
                if(asset.get('name') == "test_character_1"):
                    asset_sid = sid.copy()
                    asset_sid.shot = asset.get('name')
                    tasksAll = gazu.task.all_tasks_for_asset(asset)
                    print
                    for t in tasksAll:
                        print (t)
                    # shot_sid.seq = gazu.shot.get_sequence(shot.get('parent_id')).get('name')
                    # shot_sid.conform()
                    # print ("Shot : " + shot_sid.shot + " " + "Seq : " + shot_sid.seq)
                    # sids.append(shot_sid)

            return tasksAll
        else:
            return tasksAll

    def get_status(self, sidParam):

        sid = Sid(sidParam)  # handling the incoming sid or string # FIXME Mapping
        #sid = Sid(sid.project + '/s')
        task_status = ''

        if sid.is_shot():

            shotName = sid.shot
            projectNameCGWire = ""

            for key in project_mapping["project"]:
                if (project_mapping["project"].get(key) == sid.project):
                    projectNameCGWire = key

            project = gazu.project.get_project_by_name(projectNameCGWire)
            shots = gazu.shot.all_shots_for_project(project)
            shotFound = []

            for shot in shots:
                if(shot.get('name').lower() == shotName):
                    shotFound = shot

            tasks = gazu.task.all_tasks_for_shot(shotFound)
            task = ''
            for t in tasks:
                #print (t)
                if(t.get('task_type_name').lower() == sid.task.lower()):
                    task = t
                    #print (t.get('task_status_name'))

            #print("Tasks status")
            pprint(gazu.task.get_task_status(task))
            task_status = gazu.task.get_task_status(task)

            return task_status['short_name']

        elif sid.is_asset():

            assetName = sid.name
            print 'asset name : ' + assetName
            # TO delete!!!!
            # assetName = "crab"
            projectNameCGWire = ""
            #print("sid.task :")
            #print(sid.task)

            for key in project_mapping["project"]:
                if (project_mapping["project"].get(key) == sid.project):
                    projectNameCGWire = key

            project = gazu.project.get_project_by_name(projectNameCGWire)
            assets = gazu.asset.all_assets_for_project(project)
            assetFound = []

            for asset in assets:
                #print (asset)
                if(asset.get('name').lower() == assetName):
                    assetFound = asset
            print "ASSET FOUND :  " + str(assetFound)
            tasks = gazu.task.all_tasks_for_asset(assetFound)
            task = ''
            for t in tasks:
                # print (t)
                # print(t.get('task_type_name').lower() + " "+ sid.task.lower())
                if(t.get('task_type_name').lower() == sid.task.lower()):
                    task = t
                    #print (t.get('task_status_name'))

            #print("Tasks status : ")
            #pprint(gazu.task.get_task_status(task))
            task_status = gazu.task.get_task_status(task)

            return task_status['short_name']
        else:
            return task_status

    def set_status(self, sidParam, code_status, comment):


        sid = Sid(sidParam)  # handling the incoming sid or string # FIXME Mapping
        #sid = Sid(sid.project + '/s')
        task_status = ''

        if sid.is_shot():

            shotName = sid.shot
            # TO Delete
            # shotName = "sh01"
            projectNameCGWire = ""

            for key in project_mapping["project"]:
                if (project_mapping["project"].get(key) == sid.project):
                    projectNameCGWire = key

            project = gazu.project.get_project_by_name(projectNameCGWire)
            shots = gazu.shot.all_shots_for_project(project)
            shotFound = []

            for shot in shots:
                #print (shot)
                if(shot.get('name').lower() == shotName):
                    shotFound = shot

            tasks = gazu.task.all_tasks_for_shot(shotFound)
            task = ''
            for t in tasks:
                #print (t)
                if(t.get('task_type_name').lower() == sid.task.lower()):
                    task = t
                    #print (t.get('task_status_name'))

            # print("Tasks status")
            # pprint(gazu.task.get_task_status(task))
            task_status = gazu.task.get_task_status(task)

            gazu.task.add_comment(task,  gazu.task.get_task_status_by_short_name(code_status), comment)

        elif sid.is_asset():

            assetName = sid.name
            # TO delete!!!!
            # assetName = "test_character_1"
            projectNameCGWire = ""
            # print("sid.task :")
            # print(sid.task)

            for key in project_mapping["project"]:
                if (project_mapping["project"].get(key) == sid.project):
                    projectNameCGWire = key

            project = gazu.project.get_project_by_name(projectNameCGWire)
            assets = gazu.asset.all_assets_for_project(project)
            assetFound = []

            for asset in assets:
                # print (asset)
                if(asset.get('name').lower() == assetName):
                    assetFound = asset

            tasks = gazu.task.all_tasks_for_asset(assetFound)
            task = ''
            for t in tasks:
                # print (t)
                # print(t.get('task_type_name').lower() + " "+ sid.task.lower())
                if(t.get('task_type_name').lower() == sid.task.lower()):
                    task = t
                    # print (t.get('task_status_name'))

            # print("Tasks status : ")
            # pprint(gazu.task.get_task_status(task))
            task_status = gazu.task.get_task_status(task)

            gazu.task.add_comment(task,  gazu.task.get_task_status_by_short_name(code_status), comment)
        else:
            print("Error!!")
            pass


if __name__ == '__main__':

    from pprint import pprint
    from pipeline.libs.utils.log import setLevel, INFO, DEBUG

    sid = Sid('demo/a/01_characters/crab')

    setLevel(INFO)

    cgw = CgWire()

    for asset in cgw.all_for_project("aral"):
        print str(asset)

    """
    # cahier des charges final
    # sid = Sid('demo/a/characters/test_character_1/concept')
    print cgw.get_status(str(sid))
    cgw.set_status(sid, 'wfa', 'cool!')

    pprint(cgw.all_open_projects())
    
    print
    print 'Aral all shots'

    for asset in cgw.all_shots_for_project('aral'):
        print asset

    print
    print 'Aral all assets'

    for asset in cgw.all_assets_for_project('aral'):
        print asset

    print
    print 'Breach all assets'

    for asset in cgw.all_assets_for_project('breach'):
        print unicode(asset)

    print
    print 'Status of a shot SID'
    status_all_task = cgw.get_all_status('demo/s/s010/p030/03_anim/main/v001/p/ma');

    print
    print 'Status of a asset SID'
    status_all_task = cgw.get_all_status('demo/a/01_characters/crab/modeling/mayaa');

    print
    print 'Status of one shot SID'
    status_task = cgw.get_status('demo/s/s010/p010/layout/main');
    print (status_task)

    print
    print 'Status of one asset SID'
    status_task = cgw.get_status('demo/a/characters/test_character_1/modeling/maya/v001/w/ma');
    print (status_task)

    print
    print 'Change status of one shot SID'
    status_task = cgw.set_status('demo/s/s010/p010/layout/main', 'done', "Change status by PyCharm");
    print (status_task)

    print
    print 'Change status of one asset SID'
    status_task = cgw.set_status('demo/a/characters/test_character_1/modeling/maya/v001/w/ma', 'done', "Change status by PyCharm");
    print (status_task)


    print
    print 'User task TODO'
    user_task = gazu.user.all_tasks_to_do();
    task_0 = user_task[0]
    """
    # for task_0 in user_task:
    #     print ("Name : " + user_task["entity_name"] + " " + user_task["task_status_name"])



