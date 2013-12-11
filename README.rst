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


Install
=======

Installation goes as usual::

  $ python setup.py install


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
  public_ip: 85.114.145.182  # your public IP here
  port: 2121  # the port where the ftp server listens
  incoming_dir: /home/faltet/trth/incoming
  remove_incoming: False  # whether an incoming file should be removed after processed
  hdf5_dir: /home/faltet/trth/hdf5


You can test your credentials for TRTH by requesting the landing speed
guide page::

  $ pytrth getpage THOMSONREUTERS

If that works, then you are ready for querying TRTH and start
populating your own HDF5 files out of the CSV resulting files.

To start with, open a new terminal using tmux or similar so that the
session won't die even if the connection is lost and run the FTP
handler with::

  $ ftp_handler

Then, in another shell (not necessarily under tmux), create a new
directory for hosting the downloaded data and execute these actions::

  $ mkdir ~/trth
  $ cd ~/trth
  $ cp -r $PYTRTH_SOURCES/templates/ .
  $ cp $PYTRTH_SOURCES/samples/jobPUSH.yaml myjob.yaml

Now, edit 'myjob.yaml' and 'templates/ftpPUSH.yaml' and taylor them to
your needs.  After that, launch the query with::

  $ ftp_push myjob.yaml

That's all.  After query completion, the intermediate CSV files will
will appear in the incoming directory ('trth/incoming' in our example)
and then automagically converted into HDF5 files in the hdf5 directory
('trth/hdf5' in our example).  You can submit as many queries as you
want; just keep in mind that the ftp_handler service must always be
active.

That's all folks!  Happy TRTH querying.
