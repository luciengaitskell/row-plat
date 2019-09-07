""" Database management """

from datetime import datetime

from pymongo import MongoClient, database


class Database:
    """ Database wrapper object """
    def __init__(self, db_name):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]

    def log(self, dct, mtype=None):
        """ Log data to database with automatic time-stamping. """
        dct['ts'] = datetime.now().timestamp()
        if mtype is not None:
            dct['mtype'] = mtype
        self.db.log.insert_one(dct)
        return dct

    def close(self):
        self.client.close()
