import mock
import nose.tools as nose
import time

import jem_data.core.domain as domain
import jem_data.core.messages as messages
import jem_data.core.mongo_sink as mongo_sink

def test_writing_response_messages():
    '''Regression test for ensuring the results written to mongo stay
    compatible with the frontend's expectations.
    '''

    gateway_addr = domain.GatewayAddr(host="127.0.0.1", port=502)
    device_addr = domain.DeviceAddr(gateway_addr, 2)
    table_id = domain.TableAddr(device_addr, 3)

    msgs = [
        messages.ResponseMsg(
            table_id = table_id,
            values = [(0xC550, 5001), (0xC552, 5005)],
            timing_info = domain.TimingInfo(10000, 10001),
            error = None,
            request_info = None)
    ]

    collection = mock.Mock()

    mongo_sink._insert_into_collection(msgs, collection)
    collection.insert.assert_called_once_with([
        {
            "request_info": None,
            "timing_info": {"start": 10000, "end": 10001},
            "values": [(0xC550, 5001), (0xC552, 5005)],
            "error": None,
            "device": {
                "gateway": {
                    "host": "127.0.0.1", "port": 502
                },
                "unit": 2
            },
            "table_id": 3
        }
    ])
