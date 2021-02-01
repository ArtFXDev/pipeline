"""

Writer and Reader for User config

"""

import json
from pipeline.libs.utils.log import debug, info, error
from pipeline.libs.utils.singleton import Singleton
from pathlib2 import Path


def get_user_config_path():
    """
    Defines the user configuration path (including the conf.json file.
    Relies on Path.home()

    Returns a Path object.
    """

    home = Path.home()

    # Special Windows problem
    if not str(home).endswith('Documents') and (home / 'Documents').exists():
        home = home / 'Documents'

    user_config_path = home / 'artfx_pipeline' / 'conf.json'

    return user_config_path


user_config_path = get_user_config_path()


class ConfigIO(Singleton):
    '''
    Writer and Reader for User config
    '''

    conf_path = None

    def __init__(self):

        self.conf_path = str(user_config_path)

        # Creating file
        try:
            if not user_config_path.exists():
                user_config_path.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
                with open(self.conf_path, 'w') as conf_file:
                    json.dump({}, conf_file)
        except Exception as e:
            error('Problem creating Conf file : {} -> {}'.format(user_config_path, e))

    def save(self, key, value=None):

        data = self.read() or {}

        if value is None:
            data.pop(key, None)  # remove the key if None
        else:
            data[key] = value

        with open(self.conf_path, 'w') as conf_file:
            json.dump(data, conf_file)

    def read(self, key=None, default=None):

        data = {}
        try:
            with open(self.conf_path) as conf_file:
                data = json.load(conf_file)
        except Exception as e:
            error('Problem reading Conf file : {}'.format(e))

        if key is None:
            return data
        else:
            return data.get(key, default)


if __name__ == '__main__':

    info('Path is : {}'.format(user_config_path))

    cfio = ConfigIO()
    info(cfio.read())
    cfio.save('test', 'brief test ...')
    info(cfio.read())
    cfio.save('test', None)
    cfio.save('tested', 'OK')
    info(cfio.read())

