import json
import mock
import nose.tools as nose

import jem_data.api as api
import jem_data.core.domain as domain

def test_system_start():
    system_control_service = mock.Mock()
    app = api.app_factory(system_control_service).test_client()
    response = app.post('/system_control/start')
    nose.assert_equal(200, response.status_code)
    system_control_service.resume.assert_called_once_with()

def test_system_stop():
    system_control_service = mock.Mock()
    app = api.app_factory(system_control_service).test_client()
    response = app.post('/system_control/stop')
    nose.assert_equal(200, response.status_code)
    system_control_service.stop.assert_called_once_with()

def test_system_setup_called_once_only():
    system_control_service = mock.Mock()
    app = api.app_factory(system_control_service).test_client()
    app.post('/system_control/start')
    app.post('/system_control/start')
    system_control_service.setup.assert_called_once_with()

def test_retrieving_list_of_attached_devices():
    gateways = [
        domain.Gateway("127.0.0.1", 5020),
        domain.Gateway("192.168.0.101", 502)
    ]

    devices = [
        domain.Device(gateways[0], 0x01),
        domain.Device(gateways[0], 0x02),
        domain.Device(gateways[1], 0x01),
        domain.Device(gateways[1], 0x02),
        domain.Device(gateways[1], 0x03),
    ]

    system_control_service = mock.Mock()
    system_control_service.attached_devices.return_value = devices
    app = api.app_factory(system_control_service).test_client()
    response = app.get('/system_control/attached-devices')
    nose.assert_equal(200, response.status_code)
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))
    nose.assert_equal(len(data['gateways'][0]['devices']), 2)
    nose.assert_equal(len(data['gateways'][1]['devices']), 3)

def test_updating_list_of_attached_devices():
    gateways = [
        domain.Gateway("127.0.0.1", 5020),
        domain.Gateway("192.168.0.101", 502)
    ]

    devices = [
        domain.Device(gateways[0], 0x01),
        domain.Device(gateways[0], 0x02),
        domain.Device(gateways[1], 0x01),
        domain.Device(gateways[1], 0x02),
        domain.Device(gateways[1], 0x03),
    ]

    system_control_service = mock.Mock()
    system_control_service.update_devices.return_value = devices
    app = api.app_factory(system_control_service).test_client()
    response = app.put('/system_control/attached-devices',
        data=json.dumps([
            {'host': '127.0.0.1', 'port': 5020, 'devices': [
                {'unit': 1}, {'unit': 2}
            ]},
            {'host': '192.168.0.101', 'port': 502, 'devices': [
                {'unit': 1}, {'unit': 2}, {'unit': 3}
            ]},
        ]),
        content_type='application/json')
    system_control_service.update_devices.assert_called_once_with(devices)
    nose.assert_equal(200, response.status_code)
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))
    nose.assert_equal(len(data['gateways'][0]['devices']), 2)
    nose.assert_equal(len(data['gateways'][1]['devices']), 3)

def test_updating_devices_with_bad_data():
    app = api.app_factory(mock.Mock()).test_client()
    response = app.put('/system_control/attached-devices',
        data=json.dumps([{'foo': '127.0.0.1'}]),
        content_type='application/json')
    nose.assert_equal(400, response.status_code)
