""" Database management """

from tinydb import TinyDB
from datetime import datetime


class Database:
    """ Database wrapper object """
    def __init__(self, *args, **kwargs):
        self.db = TinyDB(*args, **kwargs)

    def log(self, dct, mtype=None):
        """ Log data to database with automatic time-stamping. """
        dct['ts'] = datetime.now().timestamp()
        if mtype is not None:
            dct['mtype'] = mtype
        self.db.insert(dct)
        return dct
