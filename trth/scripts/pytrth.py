#!/usr/bin/env python

import sys
from trth import db, api

import logging
log = logging.getLogger(__name__)

months = {
    'January': 1 , 'February': 2, 'March': 3, 'April': 4, 'May': 5,
    'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
    'November': 11, 'December': 12
    }

def expose(f):
    expose.exposed.add(f)
    return f
expose.exposed = set()

class Operations(object):
    def __init__(self):
        self._api = api.TRTHApi()
        self._api.setup()
        self._db = db.connect()

    @expose
    def resetschema(self):
        c = self._db.cursor()

        if raw_input('Are you sure you want to reset the database schema y,n? ').lower() != 'y':
            return

        with self._db:
            self._db.execute('DROP TABLE IF EXISTS expiry_months')
            self._db.execute('CREATE TABLE expiry_months (label TEXT, month TEXT, monthint INTEGER)')

            self._db.execute('DROP TABLE IF EXISTS options')
            self._db.execute('CREATE TABLE options (ric TEXT UNIQUE ON CONFLICT IGNORE)')

            self._db.execute('DROP VIEW IF EXISTS options_split')
            self._db.execute('CREATE VIEW options_split AS SELECT substr(ric, 1, 3) AS underlying, substr(ric, 4, 1) AS monthcode, CAST (substr(ric, 5, 2) AS INTEGER) AS day, CAST(substr(ric, 7, 2) AS INTEGER) AS year, CAST(substr(ric, 9, 5) AS INTEGER) AS strike, ric FROM options WHERE length(ric) = 15;')

            self._db.execute('DROP VIEW IF EXISTS options_clean')
            self._db.execute('CREATE VIEW options_clean AS SELECT o.underlying, o.day, e.monthint AS month, (CASE WHEN o.year < 90 THEN (2000 + o.year) ELSE (1900 + o.year) END) AS year, o.strike, CASE WHEN lower(o.monthcode) = o.monthcode THEN \'P\' ELSE \'C\' END AS type, o.ric FROM options_split AS o, expiry_months AS e WHERE e.label = upper(o.monthcode)')

    @expose
    def getoptionexpirymonths(self):
        expiry_months = self._api.GetOptionExpiryMonths()
        with self._db:
            self._db.execute('DELETE FROM expiry_months')
            for d in expiry_months.data:
                if d.field != 'OptionMonth':
                    continue
                for label in d.value:
                    self._db.execute('INSERT INTO expiry_months (label, month, monthint) VALUES (?,?,?)', (label, d.longName, months[d.longName]))

    @expose
    def expandoptionchain(self, base, date):
        chain = '0#%s*.U' % (base,)
        log.info('Expanding option chain for %s for date %s.', chain, date)
        options = self._api.ExpandChain(
                    self._api.Instrument(code=chain),
                    self._api.DateRange(start=date, end=date),
                    self._api.TimeRange(start='0:00:00.000',
                                        end='0:00:00.000'),
                    True)
        with self._db:
            log.info('Inserting %i rics.', len(options.instrument))
            for instrument in options.instrument:
                self._db.execute('INSERT INTO options (ric) VALUES (?)', (instrument.code,))
            log.info('Finished inserting %i rics', len(options.instrument))

    @expose
    def setftpdetails(self, hostname, username, password, path):
        print self._api.SetFTPDetails(hostname, username, password, path)

    @expose
    def testftp(self):
        print self._api.TestFTP()

    @expose
    def clearstoredchains(self):
        with self._db:
            self._db.execute('DELETE FROM options')

    @expose
    def getinflightstatus(self):
        print self._api.GetInflightStatus()
        # status = self._api.GetInflightStatus()
        # print "status:", status
        # print "active:", status.active

    @expose
    def getrequestresult(self, request_id):
        print self._api.GetRequestResult(request_id)

    @expose
    def cleanup(self):
        print self._api.CleanUp()

    @expose
    def getpage(self, ric, date=None, time=None):
        print self._api.GetPage(ric, date, time)

    def get_exposed(self):
        exposed = [f.__name__ for f in
                    expose.exposed & set(self.__class__.__dict__.values())]
        exposed.sort()
        return exposed

def main():
    logging.basicConfig(level=logging.INFO)

    operations = Operations()

    if len(sys.argv) < 2:
        print 'Usage: %s command [arg1 arg2 ...]' % (sys.argv[0],)
        print 'Available commands:'
        for exposed in operations.get_exposed():
            print '\t' + exposed
        sys.exit(1)

    getattr(operations, sys.argv[1])(*sys.argv[2:])

if __name__ == "__main__":
    main()
