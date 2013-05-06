from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('../../default.cfg')
app.config.from_envvar('JEMDATA_SETTINGS', silent=True)

import jem_data.api.views
