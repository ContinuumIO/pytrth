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

TRTH credentials are read from ~/.trth which should be a YAML file
containing the following::

  credentials:
    username: *username*
    password: *password*
  # details for the local FTP server (FTP PUSH method)
  local_ftp:
    username: trth  # the ftp username
    password: testing32  # the password for the ftp server
    ftp_addr: 0.0.0.0  # listen to everywhere
    ftp_port: 2121
    incoming_dir: /Users/faltet/ftp-trth
    remove_incoming: False  # whether an incoming file should be removed after processed
    hdf5_dir: /Users/faltet/hdf5-trth


You can test your connection to TRTH by requesting the landing speed
guide page::
  
  pytrth getpage THOMSONREUTERS
