import mock
import nose.tools as nose

import jem_data.core.domain as domain
import jem_data.services.system_control as services

def test_update_devices_validates_gateway_host():
    system_control = services.SystemControlService()
    device = domain.Device(
            unit=1,
            gateway=domain.Gateway(host=123, port=456))

    nose.assert_raises(TypeError,
                  system_control.update_devices,
                  [device])

def test_update_validates_gateway_port():
    system_control = services.SystemControlService()
    device = domain.Device(
            unit=1,
            gateway=domain.Gateway(host="127.0.0.1", port=-1))

    nose.assert_raises(ValueError,
                  system_control.update_devices,
                  [device])

def test_update_validates_device_unit():
    system_control = services.SystemControlService()
    device = domain.Device(
            unit="1",
            gateway=domain.Gateway(host="127.0.0.1", port=502))

    nose.assert_raises(TypeError,
                  system_control.update_devices,
                  [device])

def test_update_validates_device_unit_range():
    system_control = services.SystemControlService()
    device = domain.Device(
            unit=32,
            gateway=domain.Gateway(host="127.0.0.1", port=502))

    nose.assert_raises(ValueError,
                  system_control.update_devices,
                  [device])
