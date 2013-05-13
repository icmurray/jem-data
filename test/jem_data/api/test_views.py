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

def _gateways_and_devices_data():
    gateways = [
        domain.Gateway("127.0.0.1", 5020, label=None),
        domain.Gateway("192.168.0.101", 502, label=None)
    ]

    devices = [
        domain.Device(gateways[0], 0x01, label=None, tables=[]),
        domain.Device(gateways[0], 0x02, label=None, tables=[]),
        domain.Device(gateways[1], 0x01, label=None, tables=[]),
        domain.Device(gateways[1], 0x02, label=None, tables=[]),
        domain.Device(gateways[1], 0x03, label=None, tables=[]),
    ]

    return (gateways, devices)

def test_retrieving_list_of_attached_devices():
    gateways, devices = _gateways_and_devices_data()

    system_control_service = mock.Mock()
    system_control_service.attached_devices.return_value = devices
    app = api.app_factory(system_control_service).test_client()
    response = app.get('/system-control/attached-devices')
    nose.assert_equal(200, response.status_code)
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))
    nose.assert_equal(len(data['gateways'][0]['devices']), 2)
    nose.assert_equal(len(data['gateways'][1]['devices']), 3)

def test_updating_list_of_attached_devices():
    gateways, devices = _gateways_and_devices_data()

    system_control_service = mock.Mock()
    system_control_service.update_devices.return_value = devices
    app = api.app_factory(system_control_service).test_client()
    response = app.put('/system-control/attached-devices',
        data=json.dumps([
            {'host': '127.0.0.1', 'port': 5020, 'devices': [
                {'unit': 1}, {'unit': 2}
            ]},
            {'host': '192.168.0.101', 'port': 502, 'devices': [
                {'unit': 1}, {'unit': 2}, {'unit': 3}
            ]},
        ]),
        content_type='application/json')
    nose.assert_equal(200, response.status_code)
    system_control_service.update_devices.assert_called_once_with(devices)
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
            configured_gateways=[_empty_configured_gateway()],
            end_time=None,
            start_time=i)

def _empty_configured_gateway():
    return domain.ConfiguredGateway(
            host=None, port=None,
            configured_devices = [_empty_configured_device()])

def _empty_configured_device():
    return domain.ConfiguredDevice(unit=None, table_ids=[1,2,3])
