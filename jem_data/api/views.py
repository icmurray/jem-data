from jem_data.api import app

@app.route('/')
def index():
    return 'Hello World!'
