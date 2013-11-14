#
# Code that queries TRTH server and retrieves the result in-place
#
# Author: Francesc Alted
#

import time
import logging
import gzip
import base64
import trth

logging.basicConfig(level=logging.INFO)
# Setup the TRTH API
api = trth.api.TRTHApi()
api.setup()

def write_data(data, filename):
    """Write data into destination in uncompressed state."""
    data = base64.decodestring(data)
    data = gzip.io.BytesIO(data)
    data = gzip.GzipFile(fileobj=data).read()
    with open(filename, "w") as f:
        f.write(data)

template = trth.request.RequestTemplate('templates/optionTAQ.yaml')
req = trth.request.Request(template, 'BHP', 'BHP.AX', '2013-05-23',
                           ('0:00', '23:59:59.999'), '/var/tmp/bhp.csv')
    
req_id = api.SubmitRequest(req.generateRequestSpec(api))
print "request '%s' submitted" % req_id


# Wait until this request actually finishes
while True:
    status = api.GetInflightStatus()
    completed = status.completed[0]
    if req_id in completed:
        print "request '%s' completed!" % req_id
        res = api.GetRequestResult(req_id)
        write_data(res.data, req.destination)
        break
    # Prevent a possible infinite loop. Should never happen.
    if status.active == 0: break
    time.sleep(1)
