import multiprocessing
import threading
import time

import pymongo

import jem_data.core.domain as domain
import jem_data.core.exceptions as jem_exceptions
import jem_data.core.mongo_sink as mongo_sink
import jem_data.core.table_reader as table_reader
import jem_data.core.table_request_manager as table_request_manager
import jem_data.dal as dal
import jem_data.diris as diris

ValidationException = jem_exceptions.ValidationException
SystemConflict = jem_exceptions.SystemConflict

mongo_config=mongo_sink.MongoConfig(
        host='127.0.0.1',
        port=27017,
        database='jem-data')

class SystemControlService(object):
    """
    The service level api.
    
    Use an instance of this class to control the system's behaviour.
    """

    def __init__(self, db=None):
        self._status_lock = threading.RLock()
        self._table_request_manager = None
        self._db = db or dal.DataAccessLayer(mongo_config)
        self._status = {'running': False,
                        'active_recordings': []}

    def setup(self):
        self._table_request_manager =  _setup_system()
        self._db.recordings.cleanup_recordings()

    def start_recording(self, recording_config):
        '''Create a new recording, and start running it.
        '''
        with self._status_lock:
            if self._status['running']:
                raise SystemConflict(
                    "Cannot run more than one recording at a time. "
                    "Currently running: %s" % (
                        self._status['active_recordings']))

            chosen_gateways = dict(
                ((g.host, g.port), g) \
                        for g in recording_config.gateway_recording_configs)
            attached_gateways = self.attached_gateways()
            if not (set(chosen_gateways.keys()) <=
                    set((g.host, g.port) for g in attached_gateways)):
                unknown = (set(chosen_gateways.keys()) -
                           set((g.host, g.port) for g in attached_gateways))
                raise ValidationException("Unknown gateways: %r" % unknown)

            gateways = []
            for gw in attached_gateways:
                if (gw.host, gw.port) in chosen_gateways:

                    chosen_gateway = chosen_gateways[(gw.host, gw.port)]
                    chosen_devices = dict(
                        (d.unit, d) \
                            for d in chosen_gateway.device_recording_configs)

                    devices = []
                    for device in gw.devices:
                        if device.unit in chosen_devices:
                            chosen_device = chosen_devices[device.unit]

                            chosen_tables = set(chosen_device.table_ids)
                            active_tables = filter(
                                lambda t: t.id in chosen_tables,
                                device.tables)

                            new_device = device._replace(tables=active_tables)
                            devices.append(new_device)
                    new_gw = gw._replace(devices=devices)
                    gateways.append(new_gw)


            recording = domain.Recording(
                id=None,
                status='running',
                gateways=gateways,
                start_time=time.time(),
                end_time=None)

            new_recording = self._db.recordings.create(recording)

            self._status['active_recordings'].append(new_recording.id)
            self._status['running'] = True

            self._table_request_manager.start_recording(new_recording)
            return new_recording

    def resume(self):
        self._table_request_manager.resume_requests()
        self._status['running'] = True

    def stop_recording(self, recording_id):

        recording = self.get_recording(recording_id)
        if recording is None:
            return None

        with self._status_lock:
            if recording_id not in self._status['active_recordings']:
                # Nothing to do.
                return recording

            self._table_request_manager.stop_requests()

            self._status['active_recordings'].remove(recording_id)
            self._status['running'] = False

            updated_recording = self._db.recordings.end_recording(recording_id)
            return updated_recording

    def attached_gateways(self):
        '''Returns the list of `Gateway`s that the system is currently
        configured with
        '''
        return self._db.gateways.all()

    def all_recordings(self):
        '''List of all recordings.  Sorted by start date.'''
        return sorted(self._db.recordings.all(),
                      key=lambda r: r.start_time,
                      reverse=True)

    def get_recording(self, recording_id):
        '''Return the recording if it exists, otherwise None'''
        return self._db.recordings.by_id(recording_id)

    @property
    def status(self):
        '''Return's the system's current status'''
        with self._status_lock:
            d = self._status.copy()
        d.update({'now': time.time()})
        return d

    def update_gateways(self, gateways):
        '''Updates the configured gateways in bulk.

        Return the updated list if successful.  Otherwise, if validation
        fails, a `ValueError` is raised.
        '''
        for g in gateways:
            self._validate_gateway(g)
        self._db.gateways.delete_all()
        self._db.gateways.insert(gateways)
        return self.attached_gateways()

    def _validate_device(self, device):
        if not isinstance(device.unit, int):
            raise ValidationException, "Expected unit to be an integer"
        if not (0 < device.unit <= 31):
            raise ValidationException, "Unit lies outside valid range (1-31)"

    def _validate_gateway(self, gateway):
        if not isinstance(gateway.host, basestring):
            raise ValidationException, "Expected host to be string"
        if not isinstance(gateway.port, int):
            raise ValidationException, "Expected port to be an integer"
        if gateway.port <= 0:
            raise ValidationException, "Expected port to be positive"
        for device in gateway.devices:
            self._validate_device(device)

def _setup_system():
    ## Where results end up (fed to monog sink)
    results_queue = multiprocessing.Queue()

    local_gateway = domain.GatewayAddr(
            host="127.0.0.1",
            port=5020)
    local_request_queue = multiprocessing.Queue()

    remote_gateway = domain.GatewayAddr(
            host="192.168.0.101",
            port=502)
    remote_request_queue = multiprocessing.Queue()

    table_reader.start_readers(
            local_gateway,
            local_request_queue,
            results_queue,
            number_processes=2)

    table_reader.start_readers(
            remote_gateway,
            remote_request_queue,
            results_queue,
            number_processes=4)

    qs = {
            local_gateway: local_request_queue,
            remote_gateway: remote_request_queue
    }

    manager = table_request_manager.start_manager(qs)

    _setup_mongo_collections()

    mongo_writer = multiprocessing.Process(
            target=mongo_sink.mongo_writer,
            args=(results_queue, ['archive-{recording_id}', 'realtime'], mongo_config))

    mongo_writer.start()

    return manager
    
def _setup_mongo_collections():
    connection = pymongo.MongoClient(mongo_config.host, mongo_config.port)
    db = connection[mongo_config.database]

    if 'archive' not in db.collection_names():
        db.create_collection('archive')

    if 'realtime' not in db.collection_names():
        db.create_collection('realtime', size=1024*1024*100, capped=True, max=100)

