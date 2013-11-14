import suds
import functools

from time import strftime
from base64 import b64decode

from config import load_default_config

class TRTHApi(object):
    """
    A Pythonic wrapper for the TRTH Api
    WSDL interface.

    """

    def __init__(self):
        self._config = None
        self._factory = None
        self._client = None

    def setup(self, config=None):
        """
        Setups up the TRTH Api object. This must be
        called prior to using the Api object.

        """

        # Load config.
        self._config = config or load_default_config()

        # Setup WSDL objects.
        self._client = suds.client.Client(self._config.get_wsdl_url())
        self._factory = TypeFactory(self._client)

        # Set authentication credentials.
        username, password = self._config.get_credentials()
        self._client.set_options(
                soapheaders=(
                    self._factory.create('CredentialsHeader',
                                         username=username,
                                         password=password)
                )
        )
        self._valid_methods = self._client.sd[0].ports[0][0].methods.keys()
        self._valid_types = [typedef[0].name for typedef in self._client.sd[0].types]
        # print "API methods:", self._valid_methods
        # print "API types:", self._valid_types        

    def __getattr__(self, name):
        """
        Proxies method calls to the WSDL service and
        type constructors to the type factory.

        """
        return self._dispatch(name)

    def _dispatch(self, name):
        assert self._client and self._factory
        #print "dispatching: %s" % name

        if name in self._valid_methods:
            return getattr(self._client.service, name)
        elif name in self._valid_types:
            return functools.partial(self._factory.create, name)
        else:
            raise AttributeError

    def GetPage(self, ric, date=None, time=None):
        getPageFcn = self._dispatch('GetPage')

        date = date or strftime('%Y-%m-%d')
        time = time or '00:00:00'

        result = getPageFcn(ric, date, time)

        return b64decode(result.data).decode('utf-8', 'ignore')

class TypeFactory(object):
    NAMESPACE = 'ns0'
    TYPE_DEFAULTS = {
        'Instrument' : {
            'status' : None,
        }
    }

    ARRAY_MAP = {
        'Instrument' : ('ArrayOfInstrument', 'instrument'),
    }

    def __init__(self, client):
        self._client = client

    def create(self, typename, **kwargs):
        instance = self._client.factory.create('%s:%s' % (self.NAMESPACE, typename))
        # Use default args if available and merge with explicit kwargs.
        arguments = dict(self.TYPE_DEFAULTS.get(typename, {}))
        arguments.update(kwargs)

        for (k, v) in arguments.iteritems():
            setattr(instance, k, v)
        return instance

    def create_array(self, name, items):
        assert name in self.ARRAY_MAP, '%s has no valid array type.' % (name,)
        typename, containerattr = self.ARRAY_MAP[name]
        instance = self.create(typename)
        setattr(instance, containerattr, items)
        return instance
