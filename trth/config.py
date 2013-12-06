import os
import yaml

DEFAULT_CONFIG_LOCATION = os.path.expanduser('~/.trth')

TRTH_VERSION = '5.7.2'
TRTH_WSDL_URL = 'https://trth-api.thomsonreuters.com/TRTHApi-%s/wsdl/TRTHApi.wsdl' % (TRTH_VERSION,)

class Config(object):
    def __init__(self):
        self._data = None

    def load(self, location=DEFAULT_CONFIG_LOCATION):
        assert os.path.exists(location)
        self._data = yaml.load(file(location, 'rb'))

    def get_credentials(self):
        credentials = self._data['credentials']
        return credentials['username'], credentials['password']

    def get_local_ftp(self):
        return self._data['local_ftp']

    def get_wsdl_url(self):
        return TRTH_WSDL_URL

    def get_trth_version(self):
        return TRTH_VERSION


def load_default_config():
    config = Config()
    config.load()
    return config

if __name__ == '__main__':
    config = load_default_config()
    print 'TRTH API Version: %s' % (config.get_trth_version(),)
    print 'TRTH WSDL URL: %s' % (config.get_wsdl_url(),)
    print 'Username: %s Password: %s' % config.get_credentials()
