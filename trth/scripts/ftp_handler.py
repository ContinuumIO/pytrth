# Script that setups an FTP server for receiving CSV files from TRTH.
# The files will be parsed and stored in HDF5 files
#

import os, os.path
import yaml
import pandas as pd

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Read the params from configuration files
default_config = os.path.expanduser('~/.trth')
config = yaml.load(file(default_config, 'rb'))

cred_cfg = config['credentials']
ftp_cfg = config['local_ftp']

trth_user_prefix = cred_cfg['username']

ftp_addr = ftp_cfg['listen_addr']
ftp_port = int(ftp_cfg['port'])
incoming_dir = ftp_cfg['incoming_dir']
remove_incoming = bool(ftp_cfg['remove_incoming'])
hdf5_dir = ftp_cfg['hdf5_dir']
username = ftp_cfg['username']
password = ftp_cfg['password']

# Define a callback for download files
class MyHandler(FTPHandler):

    def on_file_received(self, fname):
        # Append the file into an HDF5 file
        #print "received:", fname
        if "report" in fname:
            # Do not do nothing with the report
            return
        elif fname.endswith("csv.gz"):
            df = pd.read_csv(fname, compression='gzip')
        elif fname.endswith("csv"):
            df = pd.read_csv(fname)
        else:
            # Any other extension will be ignored
            return

        # Get the name of the final HDF5 file
        fn = os.path.basename(fname)
        _, fn = fn.split(trth_user_prefix + "-")
        fn = fn[:fn.find('.')]     # remove the extension
        if '-part' in fn:
            # Get rid of the 'partXXX'
            fn = fn[:fn.rfind('-')]
        hdfname = os.path.join(hdf5_dir, fn + ".h5")

        # Open the HDFStore and append the data there
        hsb = pd.HDFStore(hdfname, complevel=9, complib='blosc')
        hsb.append('table', df, format='table', index=False)
        hsb.close()

        # Remove the downloaded file
        if remove_incoming:
            os.unlink(fname)


def main():
    # Check that incoming and hdf5 dirs are created
    if not os.path.exists(incoming_dir): os.mkdir(incoming_dir)
    if not os.path.exists(hdf5_dir): os.mkdir(hdf5_dir)

    # Setup the FTP server
    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, incoming_dir, perm="elradfmw")
    handler = MyHandler
    handler.authorizer = authorizer
    server = FTPServer((ftp_addr, ftp_port), handler)

    # And listen forever
    server.serve_forever()

if __name__ == "__main__":
    main()
