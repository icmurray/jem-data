import mock
import nose.tools as nose

import jem_data.api as api

def _create_system_mocks():
    mock_manager = mock.Mock()
    mock_setup_system = mock.Mock()
    mock_setup_system.return_value = mock_manager
    return (mock_setup_system, mock_manager)

def test_system_start():
    mock_setup_system, mock_manager = _create_system_mocks()
    app = api.app_factory(mock_setup_system).test_client()
    response = app.post('/system_control/start')
    nose.assert_equal(200, response.status_code)
    mock_manager.resume_requests.assert_called_once_with()

def test_system_stop():
    mock_setup_system, mock_manager = _create_system_mocks()
    app = api.app_factory(mock_setup_system).test_client()
    response = app.post('/system_control/stop')
    nose.assert_equal(200, response.status_code)
    mock_manager.stop_requests.assert_called_once_with()
