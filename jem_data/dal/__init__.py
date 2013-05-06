import pymongo

import jem_data.util as util

class DataAccessLayer(object):

    def __init__(self, config):
        connection = pymongo.MongoClient(config.host, config.port)
        self._db = connection[config.database]

        self.devices = DataRepository(self._db)

class DataRepository(object):

    def __init__(self, db):
        self._collection = db['devices']

    def delete_all(self):
        self._collection.remove()

    def insert(self, devices):
        self._collection.insert(map(util.deep_asdict, devices))

