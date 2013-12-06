Python Interface to the Thomson Reuters Tick History API
========================================================

**Note: This is fork of the original project in
  https://github.com/brotchie/pytrth **

**Note: This Python package is in no way affiliated with Thomson
  Reuters or any of its subsidiaries.**

pytrth provides a lite wrapper around the Thomson Reuters Tick History
(TRTH) API. A command line tool is provided to assist extraction of
options chains.

Thomson Reuters exposes a WSDL service at
https://trth-api.thomsonreuters.com/TRTHApi-$VERSION/wsdl/TRTHApi.wsdl
where $VERSION is the current API version. pytrth uses the suds
package to access this service, wrapping API object in Pythonic object
where appropriate. The TRTHApi class in src/api.py wraps this suds
interface with an even higher level interface, greatly easing the
creation of TRTH API calls.

Usage
=====

TRTH credentials and details for the FTP local server are read from
~/.trth which should be a YAML file containing the following:

# TRTH credentials:
credentials:
  username: *username*
  password: *password*
# details for the local FTP server (FTP PUSH method)
local_ftp:
  username: trth  # the ftp username
  password: testing32  # the password for the ftp server
  listen_addr: 0.0.0.0  # listen to everything
  public_ip: x.x.x.x  # your public IP here
  port: 2121
  incoming_dir: /Users/faltet/ftp-trth
  remove_incoming: False  # whether an incoming file should be removed after processed
  hdf5_dir: /home/faltet/hdf5-trth


You can test your connection to TRTH by requesting the landing speed
guide page::

  $ pytrth getpage THOMSONREUTERS

Once this works, and if you are going to use the FTP PUSH method for
downloading data (the recommended way), you must setup the local ftp
server with this script::

  $ ftp_handler

Once the FTP server is up (check the lines of the previous command),
use the next command to query the TRTH service::

  $ ftp_push myjob.yaml

where myjob.yaml is a configuration file like this:

job_name: BHP
template: templates/ftpPUSH.yaml
RICs: [BHP.AX, ]
date_range: [2013-05-23, 2013-05-24]
time_range: ['0:00', '23:59:59.999']

the ftpPUSH.yaml above is the template where you can set the full
properties of the TRTH query.  In general, you should put in the
template the invariant parameters and the rest in job file.

That's all folks!  Happy TRTH querying!
