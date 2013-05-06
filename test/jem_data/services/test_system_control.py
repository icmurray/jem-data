import mock
import nose.tools as nose

import jem_data.core.domain as domain
import jem_data.services.system_control as services
import jem_data.core.exceptions as jem_exceptions

ValidationException = jem_exceptions.ValidationException

def test_update_devices_validates_gateway_host():
    system_control = services.SystemControlService(mock.Mock())
    device = domain.Device(
            unit=1,
            gateway=domain.Gateway(host=123, port=456))

    nose.assert_raises(ValidationException,
                  system_control.update_devices,
                  [device])

def test_update_validates_gateway_port():
    system_control = services.SystemControlService(mock.Mock())
    device = domain.Device(
            unit=1,
            gateway=domain.Gateway(host="127.0.0.1", port=-1))

    nose.assert_raises(ValidationException,
                  system_control.update_devices,
                  [device])

def test_update_validates_device_unit():
    system_control = services.SystemControlService(mock.Mock())
    device = domain.Device(
            unit="1",
            gateway=domain.Gateway(host="127.0.0.1", port=502))

    nose.assert_raises(ValidationException,
                  system_control.update_devices,
                  [device])

def test_update_validates_device_unit_range():
    system_control = services.SystemControlService(mock.Mock())
    device = domain.Device(
            unit=32,
            gateway=domain.Gateway(host="127.0.0.1", port=502))

    nose.assert_raises(ValidationException,
                  system_control.update_devices,
                  [device])

def test_update_with_valid_data():
    db = mock.Mock()
    system_control = services.SystemControlService(db)
    device = domain.Device(
            unit=1,
            gateway=domain.Gateway(host="127.0.0.1", port=502))
    system_control.update_devices([device])

    db.devices.delete_all.assert_called_once_with()
    db.devices.insert.assert_called_once_with([device])
    db.devices.all.assert_called_once_with()

def test_attached_devices():
    db = mock.Mock()
    system_control = services.SystemControlService(db)
    system_control.attached_devices()
    db.devices.all.assert_called_once_with()
