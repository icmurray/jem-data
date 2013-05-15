import mock
import nose.tools as nose
import time

import jem_data.core.table_request_manager as trm
import jem_data.core.domain as domain

def test_start_recording():
    queues, config, instructions = mock.Mock(), mock.Mock(), mock.Mock()

    manager = trm.TableRequestManager(queues, config, instructions)

    recording = _stub_recording()

    expected_gateway = domain.GatewayAddr("127.0.0.1", 5020)
    expected_device = domain.DeviceAddr(expected_gateway, 10)
    expected_tables = [
        domain.TableAddr(expected_device, 1),
        domain.TableAddr(expected_device, 2),
        domain.TableAddr(expected_device, 3)
    ]

    expected_instruction = trm._ResetRequests(tables=expected_tables)
    manager.start_recording(recording)
    instructions.put.assert_called_once_with(expected_instruction)

def _stub_recording():
    return domain.Recording(
            id='abc',
            status='running',
            start_time=time.time(),
            end_time=None,
            gateways=[_stub_gateway()])

def _stub_gateway():
    return domain.Gateway(
            host="127.0.0.1", port=5020,
            label="Custom Label",
            devices=[_stub_device()])

def _stub_device():
    return domain.Device(
            unit=10,
            label='Custom Device Label',
            type='diris.a40',
            tables=[
                domain.Table(id=1, label=None, registers=[]),
                domain.Table(id=2, label=None, registers=[]),
                domain.Table(id=3, label=None, registers=[])
            ])
