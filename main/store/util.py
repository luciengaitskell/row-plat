""" Local data storage utilities. """

import os
from datetime import datetime

x = os.path.dirname(__file__)
DATA_DIR = os.path.join(x, 'data/')  # Store data in 'data' subdirectory at this module's level


def gen_name():
    """ Generate name string based on date and time. """
    cur = datetime.now()
    return cur.strftime("%y%m%dT%H%M%S")


def gen_storage_path(file_id):
    """ Generate storage path from given id string. """
    file_name = "store-{}.json".format(file_id)  # Format filename
    path = os.path.join(DATA_DIR, file_name)  # Generate full path
    return path
