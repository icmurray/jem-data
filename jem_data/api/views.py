import flask

system = flask.Blueprint('system', __name__)

@system.route('/')
def index():
    return 'Hello World!'

@system.route('/system/start', methods=['POST'])
def start_system():
    flask.current_app.table_request_manager.resume_requests()
    return 'OK'

@system.route('/system/stop', methods=['POST'])
def stop_system():
    flask.current_app.table_request_manager.stop_requests()
    return 'OK'
    
@system.before_app_first_request
def setup_system():
    manager = flask.current_app.setup_system()
    flask.current_app.table_request_manager = manager

