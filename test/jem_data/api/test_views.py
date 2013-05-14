import json
import mock
import nose.tools as nose

import jem_data.api as api
import jem_data.core.domain as domain
import jem_data.diris.devices as devices
import test.jem_data.fixtures as fixtures

def test_system_setup_called_once_only():
    system_control_service = mock.Mock()
    app = api.app_factory(system_control_service).test_client()
    app.post('/system-control/start')
    app.post('/system-control/start')
    system_control_service.setup.assert_called_once_with()

def test_retrieving_list_of_attached_gateways():
    gateways = fixtures.stub_gateways()

    system_control_service = mock.Mock()
    system_control_service.attached_gateways.return_value = gateways
    app = api.app_factory(system_control_service).test_client()
    response = app.get('/system-control/attached-devices')
    nose.assert_equal(200, response.status_code)
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))
    nose.assert_equal(len(data['gateways'][0]['devices']), 2)
    nose.assert_equal(len(data['gateways'][1]['devices']), 3)

def test_updating_list_of_attached_gateways():
    gateways = fixtures.stub_gateways()

    json_data = """\
    [
        {
            "host": "127.0.0.1",
            "port": 5020,
            "label": "Gateway 1",
            "devices": [
                {
                    "unit": 1,
                    "label": null,
                    "type": "diris.a40"
                },
                {
                    "unit": 2,
                    "label": "Custom Label",
                    "type": "diris.a40"
                }
            ]
        },

        {
            "host": "192.168.0.101",
            "port": 502,
            "label": null,
            "devices": [
                {
                    "unit": 1,
                    "label": null,
                    "type": "diris.a40"
                },
                {
                    "unit": 2,
                    "label": null,
                    "type": "diris.a40"
                },
                {
                    "unit": 3,
                    "label": null,
                    "type": "diris.a40"
                }
            ]
        }
    ]
    """

    import json
    json.loads(json_data)   # sanity check

    system_control_service = mock.Mock()
    system_control_service.update_gateways.return_value = gateways
    app = api.app_factory(system_control_service).test_client()
    response = app.put('/system-control/attached-devices',
        data=json_data,
        content_type='application/json')
    nose.assert_equal(200, response.status_code)
    system_control_service.update_gateways.assert_called_once_with(fixtures.stub_gateways())
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))
    nose.assert_equal(len(data['gateways'][0]['devices']), 2)
    nose.assert_equal(len(data['gateways'][1]['devices']), 3)

def test_updating_list_of_attached_gateways_allows_overriding():
    json_data = """\
    [
        {
            "host": "127.0.0.1",
            "port": 5020,
            "label": "Gateway 1",
            "devices": [
                {
                    "unit": 1,
                    "label": null,
                    "type": "diris.a40",
                    "tables": [
                        {
                            "id": 2,
                            "label": "Overriden label",
                            "registers": [
                                {
                                    "address": 50768,
                                    "label": "Overriden register label",
                                    "range": [-5, 5]
                                }
                            ]
                        }
                    ]
                },
                {
                    "unit": 2,
                    "label": "Custom Label",
                    "type": "diris.a40"
                }
            ]
        },

        {
            "host": "192.168.0.101",
            "port": 502,
            "label": null,
            "devices": [
                {
                    "unit": 1,
                    "label": null,
                    "type": "diris.a40"
                },
                {
                    "unit": 2,
                    "label": null,
                    "type": "diris.a40"
                },
                {
                    "unit": 3,
                    "label": null,
                    "type": "diris.a40"
                }
            ]
        }
    ]
    """

    import json
    json.loads(json_data)   # sanity check

    def id_f(v):
        return v

    system_control_service = mock.Mock()
    system_control_service.update_gateways.side_effect = id_f
    app = api.app_factory(system_control_service).test_client()
    response = app.put('/system-control/attached-devices',
        data=json_data,
        content_type='application/json')
    nose.assert_equal(200, response.status_code)
    system_control_service.update_gateways.assert_called_once_with(mock.ANY)
    data = json.loads(response.data)
    nose.assert_equal(2, len(data['gateways']))

    altered_table = data['gateways'][0]['devices'][0]['tables'][1]
    nose.assert_equal(altered_table['label'], 'Overriden label')

    altered_register = filter(
            lambda r: r['address'] == 0xC650,
            altered_table['registers'])[0]
    nose.assert_equal(altered_register['label'], 'Overriden register label')
    nose.assert_equal(altered_register['range'], [-5,5])

    unaltered_register = filter(
            lambda r: r['address'] != 0xC650,
            altered_table['registers'])[0]
    nose.assert_equal(unaltered_register['label'], hex(unaltered_register['address']))
    nose.assert_equal(unaltered_register['range'], [0,100])

def test_updating_devices_with_bad_data():
    app = api.app_factory(mock.Mock()).test_client()
    response = app.put('/system-control/attached-devices',
        data=json.dumps([{'foo': '127.0.0.1'}]),
        content_type='application/json')
    nose.assert_equal(400, response.status_code)

def test_updating_devices_with_register_not_belonging_to_given_table():
    json_data = """\
    [
        {
            "host": "127.0.0.1",
            "port": 5020,
            "label": "Gateway 1",
            "devices": [
                {
                    "unit": 1,
                    "label": null,
                    "type": "diris.a40",
                    "tables": [
                        {
                            "id": 1,
                            "label": null,
                            "registers": [
                                {
                                    "address": 50768,
                                    "label": "Overriden register label",
                                    "range": [-5, 5]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
    """

    import json
    json.loads(json_data)   # sanity check

    def id_f(v):
        return v

    system_control_service = mock.Mock()
    system_control_service.update_gateways.side_effect = id_f
    app = api.app_factory(system_control_service).test_client()
    response = app.put('/system-control/attached-devices',
        data=json_data,
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
            gateways=fixtures.stub_gateways(),
            end_time=None,
            start_time=i)
