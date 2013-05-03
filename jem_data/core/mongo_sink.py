'''
Where all the data ends up -- in mongodb.
'''

import collections
import logging

import pymongo

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
    mongo_collection.insert([_deep_asdict(msg) for msg in msgs])

def _deep_asdict(o):
    if isinstance(o, dict):
        return dict( (k, _deep_asdict(v)) for (k,v) in o.items() )
    elif hasattr(o, '_asdict'):
        return dict( (k, _deep_asdict(v)) for (k,v) in o._asdict().items() )
    else:
        return o
