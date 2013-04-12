'''Main application entry point'''

import collections
import datetime
import logging
import multiprocessing
import random
import time

import pymongo

import jem_data.core.mongo_sink as mongo_sink
import jem_data.diris.registers as registers

logging.basicConfig()
_log = logging.getLogger(__name__)

mongo_config=mongo_sink.MongoConfig(
        host='127.0.0.1',
        port=27017,
        database='jem-data')

MockResult = collections.namedtuple('MockResult',
        'device_id table_id timestamp values')

def main():

    _setup_mongo_collections()

    q1 = multiprocessing.Queue()
    q2 = multiprocessing.Queue()
    mongo_archive_writer = multiprocessing.Process(
            target=mongo_sink.mongo_writer,
            args=(q1, 'archive', mongo_config))

    mongo_stream_writer = multiprocessing.Process(
            target=mongo_sink.mongo_writer,
            args=(q2, 'realtime', mongo_config))

    queue_writer = multiprocessing.Process(
            target=_simple_queue_writer,
            args=(q1,q2))

    mongo_archive_writer.start()
    mongo_stream_writer.start()
    queue_writer.start()

def _setup_mongo_collections():
    connection = pymongo.MongoClient(mongo_config.host, mongo_config.port)
    db = connection[mongo_config.database]

    if 'archive' not in db.collection_names():
        db.create_collection('archive')
        db['archive'].create_index([('address',   pymongo.ASCENDING),
                                    ('timestamp', pymongo.ASCENDING)],
                                   unique=False,
                                   background=False)


    if 'realtime' not in db.collection_names():
        db.create_collection('realtime', size=1024*1024*100, capped=True, max=100)

def _simple_queue_writer(*qs):

    while True:
        result = MockResult(
                device_id='192.168.0.101:0xFF',
                table_id=1,
                timestamp=datetime.datetime.now(),
                values=[(addr, random.gauss(10.0, 1.5)) \
                            for addr in random.sample(
                                registers.TABLE_1.keys(), 30)])
        for q in qs:
            q.put(result)
        time.sleep(0.001)

if __name__ == '__main__':
    main()
