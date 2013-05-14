import json
import mock
import nose.tools as nose

import jem_data.api as api
import jem_data.core.domain as domain

## def test_system_start():
##     system_control_service = mock.Mock()
##     app = api.app_factory(system_control_service).test_client()
##     response = app.post('/system-control/start')
##     nose.assert_equal(200, response.status_code)
##     system_control_service.resume.assert_called_once_with()
## 
## def test_system_stop():
##     system_control_service = mock.Mock()
##     app = api.app_factory(system_control_service).test_client()
##     response = app.post('/system-control/stop')
##     nose.assert_equal(200, response.status_code)
##     system_control_service.stop.assert_called_once_with()

def test_system_setup_called_once_only():
    system_control_service = mock.Mock()
    app = api.app_factory(system_control_service).test_client()
    app.post('/system-control/start')
    app.post('/system-control/start')
    system_control_service.setup.assert_called_once_with()

def _stub_gateways():
    devices = [
        [
            domain.Device(0x01, label=None, tables=[]),
            domain.Device(0x02, label='Custom Label', tables=[]),
        ],
        [
            domain.Device(0x01, label=None, tables=[]),
            domain.Device(0x02, label=None, tables=[]),
            domain.Device(0x03, label=None, tables=[]),
        ]
    ]

    gateways = [
        domain.Gateway("127.0.0.1", 5020,
                       label='Gateway 1', devices=devices[0]),

        domain.Gateway("192.168.0.101", 502,
                       label=None, devices=devices[1])
    ]

    return (gateways, devices)

def test_retrieving_list_of_attached_devices():
    gateways = _stub_gateways()

    system_control_service = mock.Mock()
    system_control_service.attached_devices.return_value = gateways
    app = api.app_factory(system_control_service).test_client()
    response = app.get('/system-control/attached-devices')
    nose.assert_equal(200, response.status_code)
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))
    nose.assert_equal(len(data['gateways'][0]['devices']), 2)
    nose.assert_equal(len(data['gateways'][1]['devices']), 3)

def test_updating_list_of_attached_devices():
    gateways = _stub_gateways()

    system_control_service = mock.Mock()
    system_control_service.update_devices.return_value = gateways
    app = api.app_factory(system_control_service).test_client()
    response = app.put('/system-control/attached-devices',
        data=json.dumps([
            {
                'host': '127.0.0.1',
                'port': 5020,
                'label': 'Gateway 1',
                'devices': [
                    {'unit': 1, 'label': None, 'tables': [] },
                    {'unit': 2, 'label': 'Custom Label', 'tables': [] },
                ],
            },
            {
                'host': '192.168.0.101',
                'port': 502,
                'label': None,
                'devices': [
                    {'unit': 1, 'label': None, 'tables': [] },
                    {'unit': 2, 'label': None, 'tables': [] },
                    {'unit': 3, 'label': None, 'tables': [] },
                ],
            },
        ]),
        content_type='application/json')
    nose.assert_equal(200, response.status_code)
    system_control_service.update_devices.assert_called_once_with(gateways)
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))
    nose.assert_equal(len(data['gateways'][0]['devices']), 2)
    nose.assert_equal(len(data['gateways'][1]['devices']), 3)

def test_updating_devices_with_bad_data():
    app = api.app_factory(mock.Mock()).test_client()
    response = app.put('/system-control/attached-devices',
        data=json.dumps([{'foo': '127.0.0.1'}]),
        content_type='application/json')
    nose.assert_equal(400, response.status_code)

def test_getting_system_status():
    service = mock.Mock()
    service.status = {'running': True}
    app = api.app_factory(service).test_client()
    response = app.get('/system-control/status')
    nose.assert_equal(200, response.status_code)
    nose.assert_equal({'running': True}, json.loads(response.data))

def test_retrieving_list_of_recordings():
    recordings = [ _empty_recording(i) for i in xrange(10) ]

    system_control_service = mock.Mock()
    system_control_service.all_recordings.return_value = recordings
    app = api.app_factory(system_control_service).test_client()
    response = app.get('/system-control/recordings')
    nose.assert_equal(200, response.status_code)
    data = json.loads(response.data)
    nose.assert_equal(10, len(data['recordings']))

def _empty_recording(i):
    return domain.Recording(
            id=None,
            status=None,
            gateways=_stub_gateways(),
            end_time=None,
            start_time=i)
