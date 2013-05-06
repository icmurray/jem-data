import itertools

import flask

import jem_data.util as util

system_control = flask.Blueprint('system_control',
                                 __name__,
                                 url_prefix='/system_control')

@system_control.route('/')
def index():
    return 'OK'

@system_control.route('/start', methods=['POST'])
def start_system():
    flask.current_app.system_control_service.resume()
    return 'OK'

@system_control.route('/stop', methods=['POST'])
def stop_system():
    flask.current_app.system_control_service.stop()
    return 'OK'

@system_control.route('/attached-devices', methods=['GET'])
def attached_devices():
    devices = flask.current_app.system_control_service.attached_devices()
    gateways = _device_list_representation(devices)
    return flask.jsonify(gateways=gateways)

@system_control.before_app_first_request
def setup_system():
    flask.current_app.system_control_service.setup()

def _device_list_representation(devices):
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
