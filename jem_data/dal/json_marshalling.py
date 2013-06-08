'''
Marshalling json objects for mongo.
'''

import jem_data.core.domain as domain
import jem_data.core.exceptions as jem_exceptions

def unmarshall_gateway(gw_data):
    try:
        return domain.Gateway(
                host=gw_data['host'],
                port=gw_data['port'],
                label=gw_data['label'],
                devices=map(unmarshall_device,
                            gw_data['devices']))
    except Exception, e:
        raise jem_exceptions.ValidationException(str(e))

def unmarshall_device(device_data):
    return domain.Device(
            unit=device_data['unit'],
            label=device_data['label'],
            type=device_data['type'],
            tables=map(unmarshall_table, device_data['tables']))

def unmarshall_table(table_data):
    return domain.Table(
            id=table_data['id'],
            label=table_data['label'],
            registers=map(unmarshall_register, table_data['registers']))

def unmarshall_register(register_data):
    return domain.Register(
            address=register_data['address'],
            label=register_data['label'],
            range=tuple(register_data['range']),
            unit_of_measurement=register_data['unit_of_measurement'])

def unmarshall_recording(recording_data):
    return domain.Recording(
            id=str(recording_data['_id']),
            status=recording_data['status'],
            gateways=map(unmarshall_gateway,
                         recording_data['gateways']),
            start_time=recording_data['start_time'],
            end_time=recording_data['end_time'])

def unmarshall_gateway_recording_config(config_data):
    return domain.GatewayRecordingConfig(
            host=config_data['host'],
            port=config_data['port'],
            device_recording_configs=map(
                unmarshall_device_recording_config,
                config_data['configured_devices']))

def unmarshall_device_recording_config(config_data):
    return domain.DeviceRecordingConfig(
            unit=config_data['unit'],
            table_ids=config_data['table_ids'])
