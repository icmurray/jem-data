import json
import time

import flask

import jem_data
import jem_data.core.domain as domain
import jem_data.util as util
import jem_data.core.exceptions as jem_exceptions
import jem_data.dal.json_marshalling as json_marshalling
import jem_data.diris.devices as devices

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
            jem_data.dal.json_marshalling.unmarshall_gateway,
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
    updated_recording = flask.current_app.system_control_service.stop_recording(recording_id)

    if updated_recording is None:
        flask.abort(404)

    return flask.make_response(
        json.dumps(util.deep_asdict(updated_recording)), 200)

@system_control.route('/attached-devices', methods=['GET'])
def attached_devices():
    gateways = flask.current_app.system_control_service.attached_gateways()
    return flask.jsonify(gateways=_marshall_gateways(gateways))

@system_control.route('/attached-devices', methods=['PUT'])
def configure_attached_devices():
    '''Bulk update of configured devices.'''
    try:
        config = flask.request.json
        _validate_gateway_config(config)
        gateways = _merge_config_with_defaults(config)
        updated = flask.current_app.system_control_service.update_gateways(
            gateways
        )

        return flask.jsonify(gateways=_marshall_gateways(updated))
    except ValidationException, e:
        flask.abort(400)

@system_control.route('/status', methods=['GET'])
def system_status():
    status = flask.current_app.system_control_service.status
    return flask.jsonify(**status)

@system_control.before_app_first_request
def setup_system():
    flask.current_app.system_control_service.setup()

def _marshall_gateways(gateways):
    return map(util.deep_asdict, gateways)

def _unmarshall_gateways(gateways):
    try:
        return [json_marshalling.unmarshall_gateway(g) for g in gateways]
    except KeyError, e:
        raise ValidationException(str(e))
    except TypeError, e:
        raise ValidationException(str(e))

def _validate_gateway_config(config):
    for gateway in config:
        required_keys = set('host port label devices'.split())
        actual_keys = set(gateway.keys())
        if not required_keys <= actual_keys:
            raise ValidationException("Gateway data requires keys: %r" % (
                                            required_keys - actual_keys))
        for device in gateway['devices']:
            required_keys = set('unit label type'.split())
            actual_keys = set(device.keys())
            if not required_keys <= actual_keys:
                raise ValidationException(
                       "Device data requires keys: %r" % (
                            required_keys - actual_keys))

def _merge_config_with_defaults(config):
    config = config[:]
    default_device_configs = devices.ALL
    for gateway in config:
        for device in gateway['devices']:
            if device['type'] not in default_device_configs:
                raise ValidationException(
                        "Unknown device type: %s" % device['type'])

            table_defaults = dict(
                (t['id'], t) for t in util.deep_asdict(
                    default_device_configs[device['type']]))

            table_overrides = dict(
                (t['id'], t) for t in device.get('tables', []))

            _merge_tables(table_defaults, table_overrides)
            device['tables'] = table_defaults.values()

    gateways = _unmarshall_gateways(config)
    return gateways

def _merge_tables(defaults, overrides):
    '''Merges two dictionaries representing Tables.

    Only certain fields are overridable, and the registers need to be
    overridden carefully.

    Updates the default table in-place with the overridden values.
    '''

    _merge_by_field(defaults, overrides, overridable_fields=['label'])
    for id, t in defaults.items():
        if id in overrides:
            if 'registers' in overrides[id]:
                default_registers = dict(
                        (r['address'], r) for r in t['registers'])

                overrides_registers = dict(
                        (r['address'], r) for r in overrides[id]['registers'])

                if not set(overrides_registers.keys()) <= set(default_registers.keys()):
                    non_permissable_addresses = (
                        set(overrides_registers.keys()) - 
                        set(default_registers.keys()))
                    raise ValidationException(
                        "Non permissable keys in table %d: %r" % (
                            id, non_permissable_addresses))

                _merge_by_field(default_registers,
                                overrides_registers,
                                overridable_fields=['label', 'range'])
                t['registers'] = default_registers.values()

def _merge_by_field(defaults, overrides, overridable_fields):
    for id, r in defaults.items():
        if id in overrides:
            for field in overridable_fields:
                if field in overrides[id] and \
                        overrides[id][field] is not None:
                    r[field] = overrides[id][field]

