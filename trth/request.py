import yaml
import db

import logging
log = logging.getLogger(__name__)

UNSUBMITTED = 'unsubmitted'
SUBMITTED = 'submitted'
PENDINGDOWNLOAD = 'pendingdownload'
DOWNLOADING = 'downloading'
COMPLETE = 'complete'
FAILED = 'failed'

class RequestManager(object):
    def __init__(self, trth):
        self._db = db.connect(db.REQUEST_DATABASE)
        self._check_schema()
        self._trth = trth

    def _check_schema(self):
        if 'requests' not in db.get_table_names(self._db):
            with self._db:
                self._db.execute('CREATE TABLE requests (id INTEGER PRIMARY KEY AUTOINCREMENT, requestid TEXT DEFAULT NULL, name TEXT, ric TEXT, date TEXT, timestart TEXT, timeend TEXT, template TEXT, state TEXT DEFAULT \'unsubmitted\', destination TEXT, submissiontime TEXT DEFAULT CURRENT_TIMESTAMP)')

    def queue_request(self, request):
        with self._db:
            c = self._db.execute('INSERT INTO requests (name, ric, date, timestart, timeend, template, destination) VALUES (?,?,?,?,?,?,?)', (
                request.name,
                request.ric,
                request.date,
                request.timerange[0],
                request.timerange[1],
                request.template.path,
                request.destination,
            ))
            return c.lastrowid

    def process_queue(self):
        status = self._api.GetInflightStatus()
        capacity = status.limit - status.active

        log.info('Inflight Status active: %i active %i.', status.active, status.limit)

class Request(object):
    def __init__(self, template, name,
                 ric, date, timerange, destination):
        self.name = name
        self.ric = ric
        self.date = date
        self.timerange = timerange
        self.template = template
        self.destination = destination

    def generateRequestSpec(self, api):
        return api.RequestSpec(
            friendlyName=self.name,
            instrument=api.Instrument(code=self.ric),
            messageTypeList=api.ArrayOfMessageType(
                messageType=[
                    api.MessageType(name=typename,
                                    fieldList=api.ArrayOfString(
                                        string=typefields
                                    )) for typename, typefields in self.template.fields.iteritems()
            ]),
            date=self.date,
            requestInGMT=False,
            displayInGMT=False,
            timeRange=api.TimeRange(start=self.timerange[0],
                                    end=self.timerange[1]),
            requestType=self.template.requestType,
            disableHeader=self.template.disableHeader,
            marketDepth=self.template.marketDepth,
            dateFormat=self.template.dateFormat,
            disableDataPersistence=self.template.disableDataPersistence,
            includeCurrentRIC=self.template.includeCurrentRIC,
            applyCorrections=self.template.applyCorrections,
            displayMicroseconds=self.template.displayMicroseconds,
        )

class LargeRequest(object):
    def __init__(self, template, name, riclist, daterange, timerange):
        self.name = name
        self.riclist = riclist
        self.daterange = daterange
        self.timerange = timerange
        self.template = template

    def generateLargeRequestSpec(self, api):
        return api.LargeRequestSpec(
            friendlyName=self.name,
            requestType=self.template.requestType,
            instrumentList=api.ArrayOfInstrument(
                instrument=[
                    api.Instrument(code=ric) for ric in self.riclist]),
            dateRange=api.DateRange(start=self.daterange[0],
                                    end=self.daterange[1]),
            timeRange=api.TimeRange(start=self.timerange[0],
                                    end=self.timerange[1]),
            messageTypeList=api.ArrayOfMessageType(
                messageType=[
                    api.MessageType(name=typename,
                                    fieldList=api.ArrayOfString(
                                        string=typefields
                                    )) for typename, typefields in self.template.fields.iteritems()
            ]),
            requestInGMT=False,
            displayInGMT=False,
            marketDepth=self.template.marketDepth,
            splitSize=self.template.splitSize,
            delivery=self.template.delivery,
            sortType=self.template.sortType,
            fileFormat=self.template.fileFormat,
            dateFormat=self.template.dateFormat,
            disableDataPersistence=self.template.disableDataPersistence,
            includeCurrentRIC=self.template.includeCurrentRIC,
            applyCorrections=self.template.applyCorrections,
            displayMicroseconds=self.template.displayMicroseconds,
        )


class RequestTemplate(object):
    """
    Simple proxy sorrounding a yaml request
    template.

    """
    def __init__(self, path):
        self.path = path
        self._data = yaml.load(file(self.path))

    def __getattr__(self, name):
        if name not in self._data:
            raise AttributeError
        return self._data[name]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import api
    trth = api.TRTHApi()
    trth.setup()

    rm = RequestManager(trth)

    template = RequestTemplate('templates/optionTAQ.yaml')
    request = Request(template, 'BHP', 'BHP.AX', '2010-05-23', ('0:00', '23:59:59.999'), '/var/tmp/bhp.csv')

    print trth.SubmitRequest(request.generateRequestSpec(trth))
#    print rm.submit_request(request)

