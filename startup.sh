python jem_data/api/main.py &
sleep 1
curl 'http://127.0.0.1:5000/system-control/attached-devices' -X PUT -d @device-fixtures-with-sim.json -H 'content-type: application/json'
