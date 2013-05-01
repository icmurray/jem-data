from jem_data.api import app

import jem_data.core.main as main

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/system/start', methods=['POST'])
def start_system():
    main.main()
    return 'OK'
