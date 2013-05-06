import flask

import jem_data.core.main as main

def app_factory():
    app = flask.Flask(__name__)
    app.config.from_pyfile('../../default.cfg')
    app.config.from_envvar('JEMDATA_SETTINGS', silent=True)

    import jem_data.api.views as views
    app.register_blueprint(views.system)

    app.setup_system = main.setup_system

    return app
