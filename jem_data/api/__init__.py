import flask

def app_factory(system_control_service):
    app = flask.Flask(__name__)
    app.config.from_pyfile('../../default.cfg')
    app.config.from_envvar('JEMDATA_SETTINGS', silent=True)

    import jem_data.api.system_control.views as system_control
    app.register_blueprint(system_control.system_control)

    app.system_control_service = system_control_service

    return app
