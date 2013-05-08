import mock
import nose.tools as nose
import time

import jem_data.core.table_request_manager as trm
import jem_data.core.domain as domain

def test_start_recording():
    queues, config, instructions = mock.Mock(), mock.Mock(), mock.Mock()

    manager = trm.TableRequestManager(queues, config, instructions)

    recording = _stub_recording()
    gateway = domain.Gateway("127.0.0.1", 5020)
    expected_tables = [
            (domain.Device(unit=10, gateway=gateway), 1),
            (domain.Device(unit=10, gateway=gateway), 2),
            (domain.Device(unit=10, gateway=gateway), 3)]

    expected_instruction = trm._ResetRequests(tables=expected_tables)
    manager.start_recording(recording)
    instructions.put.assert_called_once_with(expected_instruction)

def _stub_recording():
    return domain.Recording(
            id='abc',
            status='running',
            start_time=time.time(),
            end_time=None,
            configured_gateways=[_stub_configured_gateway()])

def _stub_configured_gateway():
    return domain.ConfiguredGateway(
            host="127.0.0.1", port=5020,
            configured_devices=[_stub_configured_device()])

def _stub_configured_device():
    return domain.ConfiguredDevice(
            unit=10,
            table_ids=[1,2,3])
