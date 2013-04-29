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

    import jem_data.core.domain as domain
    import jem_data.core.table_reader as table_reader
    import jem_data.core.table_request_manager as table_request_manager

    request_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()

    gateway_info = domain.Gateway(
            host="127.0.0.1",
            port=5020)

    table_reader.start_readers(gateway_info, request_queue, results_queue)

    qs = {
            gateway_info: request_queue
    }

    config = {}
    for table in xrange(1,3):
        for unit in [0x01, 0x02]:
            device = domain.Device(gateway_info, unit)
            config[(device, table)] = 0.5

    table_request_manager.start_manager(qs, config)

    _setup_mongo_collections()

    mongo_writer = multiprocessing.Process(
            target=mongo_sink.mongo_writer,
            args=(results_queue, ['archive', 'realtime'], mongo_config))

    mongo_writer.start()

def _setup_mongo_collections():
    connection = pymongo.MongoClient(mongo_config.host, mongo_config.port)
    db = connection[mongo_config.database]

    if 'archive' not in db.collection_names():
        db.create_collection('archive')

    if 'realtime' not in db.collection_names():
        db.create_collection('realtime', size=1024*1024*100, capped=True, max=100)

if __name__ == '__main__':
    main()
