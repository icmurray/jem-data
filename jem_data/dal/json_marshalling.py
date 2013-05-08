'''
Marshalling json objects for mongo.
'''

import jem_data.core.domain as domain
import jem_data.core.exceptions as jem_exceptions

def extract_configured_gateway(configured_gw_data):
    try:
        return domain.ConfiguredGateway(
                host=configured_gw_data['host'],
                port=configured_gw_data['port'],
                configured_devices=map(
                    extract_configured_device,
                    configured_gw_data['configured_devices']))
    except Exception, e:
        raise jem_exceptions.ValidationException(str(e))

def extract_configured_device(configured_device_data):
    return domain.ConfiguredDevice(**configured_device_data)

def unmarshall_recording(recording_data):
    return domain.Recording(
            id=str(recording_data['_id']),
            status=recording_data['status'],
            configured_gateways=map(
                extract_configured_gateway,
                recording_data['configured_gateways']),
            start_time=recording_data['start_time'],
            end_time=recording_data['end_time'])

