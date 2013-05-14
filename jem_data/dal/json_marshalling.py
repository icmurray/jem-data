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
    return domain.Device(**device_data)

def unmarshall_recording(recording_data):
    return domain.Recording(
            id=str(recording_data['_id']),
            status=recording_data['status'],
            gateways=map(unmarshall_gateway,
                         recording_data['gateways']),
            start_time=recording_data['start_time'],
            end_time=recording_data['end_time'])

