import collections

import pymongo

import jem_data.core.domain as domain
import jem_data.util as util

class DataAccessLayer(object):

    def __init__(self, config):
        connection = pymongo.MongoClient(config.host, config.port)
        self._db = connection[config.database]

        self.devices = DeviceRepository(self._db)

class DeviceRepository(object):

    def __init__(self, db):
        self._collection = db['devices']

    def delete_all(self):
        self._collection.remove()

    def insert(self, devices):
        self._collection.insert(map(util.deep_asdict, devices))

    def all(self):
        devices = []
        for device in self._collection.find():
            gateway = domain.Gateway(
                host=device['gateway']['host'],
                port=device['gateway']['port'])

            devices.append(domain.Device(
                unit=device['unit'],
                gateway=gateway))
        return devices
