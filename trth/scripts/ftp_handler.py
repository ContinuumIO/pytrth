# Script that setups an FTP server for receiving CSV files from TRTH.
# The files will be parsed and stored in HDF5 files
#

import os.path
import pandas as pd

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

trth_user_prefix = "francesc@continuum.io"
ftp_addr = "0.0.0.0"   # means listen from everywhere
ftp_port = 2121
incoming_dir = "/Users/faltet/ftp-trth"
incoming_remove = False  # whether the processed incoming file should removed
hdf5_dir = "/Users/faltet/hdf5"
username = "trth"
password = "testing32"

class MyHandler(FTPHandler):

    def on_file_received(self, file):
        # Append the file into an HDF5 file
        #print "received:", file
        if file.endswith("csv.gz"):
            df = pd.read_csv(file, compression='gzip')
        elif file.endswith("csv"):
            df = pd.read_csv(file)
        else:
            # Any other extension will be ignored
            return

        # Get the name of the file
        hdfname = os.path.basename(file)
        _, hdfname = hdfname.split(trth_user_prefix + "-")
        hdfname = os.path.join(hdf5_dir, hdfname + ".h5")

        # Open the HDFStore and append the data there
        hsb = pd.HDFStore(hdfname, complevel=9, complib='blosc')
        hsb.append('table', df, format='table', index=False)
        hsb.close()

        # Remove the downloaded file
        if remove_incoming:
            os.unlink(file)

if __name__ == "__main__":
    # Check that incoming and hdf5 dirs are created
    if not os.path.exists(incoming_dir): os.mkdir(incoming_dir)
    if not os.path.exists(hdf5_dir): os.mkdir(hdf5_dir)
    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, incoming_dir, perm="elradfmw")

    handler = MyHandler
    handler.authorizer = authorizer

    server = FTPServer((ftp_addr, ftp_port), handler)
    server.serve_forever()
