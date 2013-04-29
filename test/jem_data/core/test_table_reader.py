import mock
import nose.tools as nose

import jem_data.core.domain as domain
import jem_data.core.messages as messages
import jem_data.core.table_reader as table_reader

def test_read_small_table():
    in_q = mock.Mock()
    in_q.get.return_value = messages.ReadTableMsg(
            device_id = domain.DeviceId(1L, 0xFF),
            table_id = 1)

    out_q = mock.Mock()
    conn = mock.Mock()

    with mock.patch('jem_data.core.modbus.read_registers'):
        table_reader._read_table(in_q, out_q, conn)

    out_q.put.assert_called_once_with(mock.ANY)

def test_read_large_table():
    in_q = mock.Mock()
    in_q.get.return_value = messages.ReadTableMsg(
            device_id = domain.DeviceId(1L, 0xFF),
            table_id = 6)

    out_q = mock.Mock()
    conn = mock.Mock()

    with mock.patch('jem_data.core.modbus.read_registers'):
        table_reader._read_table(in_q, out_q, conn)

    ## Table 6 is large, and requires more than 1 call.
    ## Check that more than 1 sub-result is being pushed on the queue.
    nose.assert_greater(len(out_q.put.mock_calls), 1)
