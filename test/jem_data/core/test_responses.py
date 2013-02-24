import mock
import nose.tools as nose

import jem_data.core.response as response

def test_access_value_of_a_multi_register_value():
    jem_response = response.RegisterResponse(
            pymodbus_response = _mock_pymodbus_response(),
            requested_registers = _requested_registers())

    result = jem_response.read_register(0xC550)
    nose.assert_equal(result, 0xABCD1234)

def test_access_value_of_a_single_register_value():
    jem_response = response.RegisterResponse(
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
