# -*- coding: utf-8 -*-

"""

"""

import heapq
import multiprocessing
import time

import jem_data.core.messages as messages

def start_manager(queues, config):
    """
    Create and start a new table request manager processes.

    :param queues: is a mapping from `Gateway` to `Queue` objects.
    :param config: is a mapping from `(Device,int)` to floats.

    The `queues` parameter holds the input queues for each `Gateway`.  These
    are used to write new requests to.

    The `config` parameter holds the target delay between requests for each
    `Device` and table pairing.
    """

    p = multiprocessing.Process(
            target = _run,
            args = (queues, config))
    p.start()

def _run(queues, config):

    if not config:
        raise ValueError("Empty configuration!")

    now = time.time()
    tasks = [ _heap_item(table, config, now) for table in config ]
    heapq.heapify(tasks)

    while True:
        _wakeup_at(tasks[0][0])

        (_, table) = heapq.heappop(tasks)
        heapq.heappush(tasks, _heap_item(table, config))
        _push_request(table, queues)

def _heap_item(table, config, now=None):
    now = now or time.time()
    return (now + config[table], table)

def _push_request(table, queues):
    device, table_id = table
    q = queues[device.gateway]
    req = messages.ReadTableMsg(
            device_id = device,
            table_id = table_id)
    q.put(req)

def _wakeup_at(t):
    "A rough approximation.  Absolute precision is not necessary"
    now = time.time()
    if t > now:
        time.sleep(t - now)
