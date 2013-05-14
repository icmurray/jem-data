import time

import bson.objectid as objectid
import pymongo

import jem_data.core.exceptions as jem_exceptions
import json_marshalling
import jem_data.util as util

class DataAccessLayer(object):

    def __init__(self, config):
        connection = pymongo.MongoClient(config.host, config.port)
        self._db = connection[config.database]

        self.gateways = GatewayRepository(self._db)
        self.recordings = RecordingsRepository(self._db)

class GatewayRepository(object):

    def __init__(self, db):
        self._collection = db['gateways']

    def delete_all(self):
        self._collection.remove()

    def insert(self, gateways):
        self._collection.insert(map(util.deep_asdict, gateways))

    def all(self):
        return [ json_marshalling.unmarshall_gateway(d) for d in self._collection.find() ]

class RecordingsRepository(object):

    def __init__(self, db):
        self._db = db
        self._collection = db['recordings']

    def all(self):
        recordings = []
        for recording_data in self._collection.find():
            r = json_marshalling.unmarshall_recording(recording_data)
            recordings.append(r)
        return recordings

    def by_id(self, recording_id):
        data = self._collection.find_one(objectid.ObjectId(recording_id))
        if data is None:
            return None

        return json_marshalling.unmarshall_recording(data)

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

    def end_recording(self, recording_id):
        '''End the given recording'''
        now = time.time()
        spec = {'_id': objectid.ObjectId(recording_id)}
        doc  = {'$set': {'status': 'ended', 'end_time': now}}
        result = self._collection.update(spec, doc)
        if result['err'] is None:
            return self.by_id(recording_id)
        else:
            raise jem_exceptions.PersistenceException(result['err'])


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
        
