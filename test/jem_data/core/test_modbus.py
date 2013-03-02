import mock
import nose.tools as nose

import jem_data.core.modbus as modbus

def test_read_registers_requests_the_correct_address_range():
    registers = {
        0xC550: 2,
        0xC552: 2,
        0xC556: 3
    }

    client = mock.Mock()
    modbus.read_registers(client, unit=0x01, registers=registers)
    client.read_holding_registers.assert_called_once_with(
            0xC550-1,
            0xC559-0xC550,
            unit=0x01)

def test_read_registers_checks_for_large_register_range():
    registers = {
        1: 1,
        126: 1,
    }

    client = mock.Mock()
    nose.assert_raises(modbus.InvalidModbusRangeException,
                       modbus.read_registers,
                       client, unit=0x01, registers=registers)
    nose.assert_equal(client.read_holding_registers.call_count, 0)

def test_read_registers_includes_word_size_when_calculating_range():
    registers = {
        1: 126
    }

    client = mock.Mock()
    nose.assert_raises(modbus.InvalidModbusRangeException,
                       modbus.read_registers,
                       client, unit=0x01, registers=registers)
    nose.assert_equal(client.read_holding_registers.call_count, 0)

def test_read_register_range_exactly_right_edge_case():
    registers = {
        1: 1,
        124: 2,
    }

    client = mock.Mock()
    modbus.read_registers(client, unit=0x01, registers=registers)
    client.read_holding_registers.assert_called_once_with(0, 125, unit=0x01)

def test_access_value_of_a_multi_register_value():
    jem_response = modbus.RegisterResponse(
            pymodbus_response = _mock_pymodbus_response(),
            requested_registers = _requested_registers())

    result = jem_response.read_register(0xC550)
    nose.assert_equal(result, 0xABCD1234)

def test_access_value_of_a_single_register_value():
    jem_response = modbus.RegisterResponse(
            pymodbus_response = _mock_pymodbus_response(),
            requested_registers = _requested_registers())

    result = jem_response.read_register(0xC553)
    nose.assert_equal(result, 0x22)

#---------------------------------------------------------------------------# 
# Fixture data and functions
#---------------------------------------------------------------------------# 

def _requested_registers():
    return {
        0xC550: 2,
        0xC552: 1,
        0xC553: 1,
    }

def _mock_pymodbus_response():

    register_values = {
        0xC550: 0xABCD,
        0xC551: 0x1234,
        0xC552: 0,
        0xC553: 0x22
    }
    def side_effect(addr):
        return register_values[addr + 0xC550]

    m = mock.Mock()
    m.getRegister = mock.MagicMock(side_effect=side_effect)
    return m
