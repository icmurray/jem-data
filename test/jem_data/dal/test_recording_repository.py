import mock
import nose.tools as nose
import time

import jem_data.core.domain as domain
import jem_data.core.exceptions as jem_exceptions
import jem_data.dal as dal
import test.jem_data.fixtures as fixtures

def test_create():

    def add_id_to_dict(d):
        d['_id'] = 'abcdefg'

    db = mock.MagicMock()
    db['recordings'].insert.side_effect = add_id_to_dict
    repo = dal.RecordingsRepository(db)
    recording = domain.Recording(
            id=None,
            status='running',
            gateways=fixtures.stub_gateways(),
            start_time=time.time(),
            end_time=None)
    updated_value = repo.create(recording)

    db['recordings'].insert.assert_called_once_with(mock.ANY)
    db.create_collection.assert_called_once_with('archive-abcdefg')
    nose.assert_equal(updated_value.id, 'abcdefg')

def test_all():
    raw_data = {
        '_id': 'abcde',
        'status': 'running',
        'start_time': time.time(),
        'end_time': None,
        'gateways': [
            {
                'host': '127.0.0.1',
                'port': 5020,
                'label': 'Gateway 1',
                'devices': [
                    {'unit': 1, 'label': 'Device One', 'type': 'diris.a40',
                     'tables': [
                          {'id': 1, 'label': 'Table One',
                           'registers': [
                               {
                                   'address': 0xC550,
                                   'label': 'Current or something',
                                   'range': (-100,100)
                               },
                           ]
                          },
                          {'id': 2, 'label': 'Table Two',
                           'registers': []
                          }
                     ],
                    },
                    {'unit': 2, 'label': 'Device Two', 'type': 'diris.a40',
                     'tables': [
                          {'id': 1, 'label': 'Table One',
                           'registers': []
                          },
                     ]
                    },
                ]
            },
            {
                'host': '192.168.0.101',
                'port': 502,
                'label': 'Gateway 2',
                'devices': []
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
