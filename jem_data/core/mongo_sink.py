'''
Where all the data ends up -- in mongodb.
'''

import collections
import logging

import pymongo

import jem_data.util as util

MongoConfig = collections.namedtuple('MongoConfig',
        'host port database')

logging.basicConfig()
_log=logging.getLogger(__name__)

def mongo_writer(q, collection_names, mongo_config):
    '''Endlessly reads data from a Queue, and writes it to mongo.'''

    connection = pymongo.MongoClient(mongo_config.host, mongo_config.port)
    db = connection[mongo_config.database]

    while True:
        try:
            msg = q.get()
            for collection_name in collection_names:
                _insert_into_collection([msg], db[collection_name])
        except pymongo.errors.AutoReconnect, e:
            _log.error("Connection to mongo lost.  Auto-reconnect will be attempted")
        except pymongo.errors.ConnectionFailure, e:
            _log.error("Connection failure")
        except Exception, e:
            _log.error(e)

def _insert_into_collection(msgs, mongo_collection):
    '''Write a bunch of messages to the given collection.

    Massages the data into the form expected to be stored.  Ie, if the domain
    model changes, then this step keeps backward-compatibility.
    '''
    ds = [util.deep_asdict(msg) for msg in msgs]

    # Rename a few fields, and promote some data up a level.
    for d in ds:
        d['device'] = d['table_id']['device_addr']
        d['device']['gateway'] = d['device']['gateway_addr']
        del d['device']['gateway_addr']
        d['table_id'] = d['table_id']['id']
    mongo_collection.insert(ds)
