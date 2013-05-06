import flask

from jem_data.api import app

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/system/start', methods=['POST'])
def start_system():
    flask.current_app.table_request_manager.resume_requests()
    return 'OK'

@app.route('/system/stop', methods=['POST'])
def stop_system():
    flask.current_app.table_request_manager.stop_requests()
    return 'OK'
