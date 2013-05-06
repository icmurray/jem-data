import flask
app = flask.Flask(__name__)
app.config.from_pyfile('../../default.cfg')
app.config.from_envvar('JEMDATA_SETTINGS', silent=True)

@app.before_first_request
def setup_system():
    import jem_data.core.main as main
    manager = main.setup_system()
    flask.current_app.table_request_manager = manager

import jem_data.api.views
