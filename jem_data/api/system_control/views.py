import flask

system_control = flask.Blueprint('system_control',
                                 __name__,
                                 url_prefix='/system_control')

@system_control.route('/')
def index():
    return 'OK'

@system_control.route('/start', methods=['POST'])
def start_system():
    flask.current_app.table_request_manager.resume_requests()
    return 'OK'

@system_control.route('/stop', methods=['POST'])
def stop_system():
    flask.current_app.table_request_manager.stop_requests()
    return 'OK'
    
@system_control.before_app_first_request
def setup_system():
    manager = flask.current_app.setup_system()
    flask.current_app.table_request_manager = manager

