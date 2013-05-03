# -*- coding: utf-8 -*-

"""

"""

import heapq
import multiprocessing
import time

import jem_data.core.messages as messages

def start_manager(queues, config, instruction_queue=None):
    """
    Create and start a new table request manager processes.

    :param queues: is a mapping from `Gateway` to `Queue` objects.
    :param config: is a mapping from `(Device,int)` to floats.
    :param instruction_queue: is an optional `Queue` that the new process will
                              listen for command messages on.  If `None` is
                              given, then this function will create a new
                              `multiprocessing.Queue`.
    :return: the `Queue` that the new `Process` will listen for command
             messages on.  This is the same as `instruction_queue` if that is
             given, otherwise it is the newly created `multiprocessing.Queue`.

    The `queues` parameter holds the input queues for each `Gateway`.  These
    are used to write new requests to.

    The `config` parameter holds the target delay between requests for each
    `Device` and table pairing.

    The `instruction_queue` is a reference to a `Queue` that the newly created
    process will listen to command messages upon.
    """
    if instruction_queue is None:
        instruction_queue = multiprocessing.Queue()
    p = multiprocessing.Process(
            target = _run,
            args = (queues, config, instruction_queue))
    p.start()
    return instruction_queue

def _run(queues, config, instruction_queue):

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
            device = device,
            table_id = table_id)
    q.put(req)

def _wakeup_at(t):
    "A rough approximation.  Absolute precision is not necessary"
    now = time.time()
    if t > now:
        time.sleep(t - now)
