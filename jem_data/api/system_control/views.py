import itertools
import json
import time

import flask

import jem_data
import jem_data.core.domain as domain
import jem_data.util as util
import jem_data.core.exceptions as jem_exceptions

ValidationException = jem_exceptions.ValidationException

system_control = flask.Blueprint('system_control',
                                 __name__,
                                 url_prefix='/system-control')

@system_control.route('/')
def index():
    return 'OK'

@system_control.route('/recordings', methods=['GET'])
def list_recordings():
    recordings = flask.current_app.system_control_service.all_recordings()
    recordings = map(util.deep_asdict, recordings)
    return flask.jsonify(recordings=recordings)

@system_control.route('/recordings', methods=['POST'])
def start_recording():
    configured_gateways = map(
            jem_data.dal.json_marshalling.extract_configured_gateway,
            flask.request.json)
    recording = domain.Recording(
            id=None,
            status='running',
            configured_gateways = configured_gateways,
            start_time=time.time(),
            end_time=None)
    try:
        updated_recording = flask.current_app.system_control_service.start_recording(recording)
        return flask.make_response(json.dumps(util.deep_asdict(updated_recording)), 201)
    except jem_exceptions.SystemConflict, e:
        flask.abort(409)

@system_control.route('/recordings/<recording_id>', methods=['GET'])
def recording_details(recording_id):
    recording = flask.current_app.system_control_service.get_recording(
            recording_id)
    if recording is not None:
        return flask.make_response(
            json.dumps(util.deep_asdict(recording)), 200)
    else:
        flask.abort(404)

@system_control.route('/recordings/<recording_id>/stop', methods=['PUT'])
def stop_recording(recording_id):
    raise NotImplemented, "Not yet implemented"

@system_control.route('/attached-devices', methods=['GET'])
def attached_devices():
    devices = flask.current_app.system_control_service.attached_devices()
    gateways = _marshall_device_list(devices)
    return flask.jsonify(gateways=gateways)

@system_control.route('/attached-devices', methods=['PUT'])
def configure_attached_devices():
    '''Bulk update of configured devices.'''
    gateways = flask.request.json
    try:
        devices = _unmarshall_device_list(gateways)
        updated = flask.current_app.system_control_service.update_devices(
            devices
        )

        return flask.jsonify(gateways=_marshall_device_list(updated))
    except ValidationException, e:
        flask.abort(400)

@system_control.route('/status', methods=['GET'])
def system_status():
    status = flask.current_app.system_control_service.status
    return flask.jsonify(**status)

@system_control.before_app_first_request
def setup_system():
    flask.current_app.system_control_service.setup()

def _marshall_device_list(devices):
    '''REST API's device list representation'''

    def get_gateway(d):
        return d.gateway

    ds = sorted(devices, key=get_gateway)
    gateways = []
    for gateway, devices in itertools.groupby(ds, get_gateway):
        gw_dict = util.deep_asdict(gateway)
        dev_dics = map(util.deep_asdict, devices)
        gw_dict['devices'] = dev_dics
        gateways.append(gw_dict)

    return gateways

def _unmarshall_device_list(gateways):
    '''Unpick devices from list of gateways'''
    try:
        devices = []
        for gw_dict in gateways:
            gateway = domain.Gateway(
                    host=gw_dict['host'],
                    port=gw_dict['port'])
            for dev_dict in gw_dict['devices']:
                d = domain.Device(gateway=gateway, unit=dev_dict['unit'])
                devices.append(d)
        return devices
    except KeyError, e:
        raise ValidationException, str(e)
    except TypeError, e:
        raise ValidationException, str(e)
