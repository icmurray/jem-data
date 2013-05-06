import mock
import nose.tools as nose

import jem_data.api as api

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

