'''
Where all the data ends up -- in mongodb.
'''

import collections
import logging

import pymongo

MongoMessage = collections.namedtuple('MongoMessage',
        'device_id table_id timestamp address value')

MongoConfig = collections.namedtuple('MongoConfig',
        'host port database')

logging.basicConfig()
_log=logging.getLogger(__name__)

def mongo_writer(q, collection_name, mongo_config):
    '''Endlessly reads data from a Queue, and writes it to mongo.'''

    connection = pymongo.MongoClient(mongo_config.host, mongo_config.port)
    db = connection[mongo_config.database]
    mongo_collection = db[collection_name]

    while True:
        try:
            result = q.get()
            msgs = _split_result(result)
            _insert_into_collection(msgs, mongo_collection)
        except pymongo.errors.AutoReconnect, e:
            _log.error("Connection to mongo lost.  Auto-reconnect will be attempted")
        except pymongo.errors.ConnectionFailure, e:
            _log.error("Connection failure")
        except Exception, e:
            _log.error(e)

def _split_result(result):
    '''Splits a modbus result to a list of MongoMessage instances'''
    return [ MongoMessage(
                device_id=result.device_id,
                table_id=result.table_id,
                timestamp=result.timestamp,
                address=address,
                value=value) for (address,value) in result.values ]

def _insert_into_collection(msgs, mongo_collection):
    mongo_collection.insert([msg._asdict() for msg in msgs])
