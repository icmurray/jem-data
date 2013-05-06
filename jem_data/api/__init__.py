import flask

import jem_data.core.main as main

def app_factory(setup_system=main.setup_system):
    app = flask.Flask(__name__)
    app.config.from_pyfile('../../default.cfg')
    app.config.from_envvar('JEMDATA_SETTINGS', silent=True)

    import jem_data.api.system_control.views as system_control
    app.register_blueprint(system_control.system_control)

    app.setup_system = setup_system

    return app
