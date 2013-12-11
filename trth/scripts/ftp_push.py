#
# Script that queries TRTH server using the FTP PUSH method
#
# Author: Francesc Alted
# Date: 2013-12-06

import logging
import yaml
import sys

import trth

def main():
    if len(sys.argv) == 1:
        print "Pass the job YAML file"
        sys.exit()

    job_file = sys.argv[1]
    job = yaml.load(file(job_file, 'rb'))

    logging.basicConfig(level=logging.INFO)
    # Setup the TRTH API
    api = trth.api.TRTHApi()
    api.setup()

    # Read the template data
    template = trth.request.RequestTemplate(job['template'])

    if template.delivery == "Push":
        # Specify the details of the FTP server
        fl = api._config.get_local_ftp()
        api.SetFTPDetails("%s:%s" % (fl['public_ip'], fl['port']),
                          fl['username'], fl['password'], None)

    # Build the request
    req = trth.request.LargeRequest(
        template, job['job_name'], job['RICs'],
        job['date_range'], job['time_range'])
    large_req = req.generateLargeRequestSpec(api)

    # Submit it
    req_id = api.SubmitFTPRequest(large_req)
    print "request '%s' submitted" % req_id

if __name__ == "__main__":
    main()
