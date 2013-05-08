import mock
import nose.tools as nose
import time

import jem_data.core.domain as domain
import jem_data.core.exceptions as jem_exceptions
import jem_data.dal as dal

def test_insert():

    def add_id(d):
        d['_id'] = 'abcdefg'

    db = {'recordings': mock.Mock()}
    db['recordings'].insert.side_effect = add_id
    repo = dal.RecordingsRepository(db)
    recording = domain.Recording(
            id=None,
            status='running',
            configured_gateways=[_configured_gateway()],
            start_time=time.time(),
            end_time=None)
    updated_value = repo.insert(recording)

    db['recordings'].insert.assert_called_once_with(mock.ANY)
    nose.assert_equal(updated_value.id, 'abcdefg')

def test_all():
    raw_data = {
        '_id': 'abcde',
        'status': 'running',
        'start_time': time.time(),
        'end_time': None,
        'configured_gateways': [
            {
                'host': '127.0.0.1',
                'port': 5020,
                'configured_devices': [
                    {'unit': 1, 'table_ids': [1,2,6]},
                    {'unit': 2, 'table_ids': [1,2]},
                ]
            },
            {
                'host': '192.168.0.101',
                'port': 502,
                'configured_devices': [
                    {'unit': 5, 'table_ids': [1,2,6]},
                    {'unit': 6, 'table_ids': []},
                ]

            }
        ]
    }
    
    db = {'recordings': mock.Mock()}
    db['recordings'].find.return_value = [raw_data]
    repo = dal.RecordingsRepository(db)
    result = repo.all()
    nose.assert_true(result)
    nose.assert_true(isinstance(result[0], domain.Recording))


def test_cleanup_recordings():
    db = {'recordings': mock.Mock()}
    db['recordings'].update.return_value = { 'err': None, 'n': 5 }
    repo = dal.RecordingsRepository(db)
    result = repo.cleanup_recordings()
    nose.assert_equal(result, 5)

def test_cleanup_recordings_raise_exceptions_on_error():
    db = {'recordings': mock.Mock()}
    db['recordings'].update.return_value = { 'err': "Uh oh" }
    repo = dal.RecordingsRepository(db)
    nose.assert_raises(jem_exceptions.PersistenceException,
                       repo.cleanup_recordings)

def _configured_device():
    return domain.ConfiguredDevice(
            unit=10,
            table_ids=[1,2,6])

def _configured_gateway():
    return domain.ConfiguredGateway(
            host="127.0.0.1",
            port=5020,
            configured_devices=[_configured_device()])
