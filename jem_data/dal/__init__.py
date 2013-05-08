import time

import pymongo

import jem_data.core.domain as domain
import jem_data.core.exceptions as jem_exceptions
import json_marshalling
import jem_data.util as util

class DataAccessLayer(object):

    def __init__(self, config):
        connection = pymongo.MongoClient(config.host, config.port)
        self._db = connection[config.database]

        self.devices = DeviceRepository(self._db)
        self.recordings = RecordingsRepository(self._db)

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

class RecordingsRepository(object):

    def __init__(self, db):
        self._db = db
        self._collection = db['recordings']

    def all(self):
        recordings = []
        for recording_data in self._collection.find():
            r = domain.Recording(
                    id=str(recording_data['_id']),
                    status=recording_data['status'],
                    configured_gateways=map(
                        json_marshalling.extract_configured_gateway,
                        recording_data['configured_gateways']),
                    start_time=recording_data['start_time'],
                    end_time=recording_data['end_time'])
            recordings.append(r)
        return recordings

    def create(self, recording):
        '''Inserts a new recording, and creates a collection for its results.
        '''
        data = util.deep_asdict(recording)
        self._collection.insert(data)
        new_id = str(data['_id'])

        try:
            self._db.create_collection('archive-%s' % new_id)
        except pymongo.errors.CollectionInvalid, e:
            raise jem_exceptions.PersistenceException(str(e))

        return recording._replace(id=new_id)

    def cleanup_recordings(self):
        '''Check for any running recordings, and mark as aborted.

        This is meant to be run at the startup of the system in case it
        previously crashed.  In such a case, any running recordings will no
        longer be running, but will still be marked as such in the database.
        Hence this function.
        '''
        now = time.time()
        spec = {'status': 'running'}
        doc  = {'$set': {'status': 'aborted', 'end_time': now}}
        result = self._collection.update(spec, doc, multi=True)
        if result['err'] is None:
            return result['n']
        else:
            raise jem_exceptions.PersistenceException(result['err'])
        
