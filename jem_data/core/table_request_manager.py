# -*- coding: utf-8 -*-

"""

"""

import collections
import heapq
import multiprocessing
import time

import jem_data.core.messages as messages

class TableRequestManager(multiprocessing.Process):

    def __init__(self, queues, config, instructions):
        super(TableRequestManager, self).__init__()
        self._queues = queues.copy()
        self._config = config.copy()
        self._instructions = instructions
        self._tasks = []

    def run(self):
        if not self._config:
            raise ValueError("Empty configuration!")

        now = time.time()
        for table in self._config:
            self._enqueue_push_table_request_task(table, now=now)
        self._enqueue_read_instructions_task()

        while True:
            _wakeup_at(self._tasks[0][0])

            (_, task) = heapq.heappop(self._tasks)
            self._run_task(task)

    def _run_task(self, task):
        if isinstance(task, _PushTableRequestTask):
            self._run_push_table_request_task(task)
        elif isinstance(task, _ReadInstructionsTask):
            self._run_read_instructions_task(task)
        else:
            raise ValueError("Unknown Task Type: %s" % task)

    def _run_push_table_request_task(self, task):
        device, table_id = task.device, task.table_id
        q = self._queues[device.gateway]
        req = messages.ReadTableMsg(
                device = device,
                table_id = table_id)
        q.put(req)
        self._enqueue_push_table_request_task((device, table_id))

    def _run_read_instructions_task(self, task):
        self._enqueue_read_instructions_task()

    def _enqueue_push_table_request_task(self, table, now=None):
        task = _PushTableRequestTask(*table)
        delay = self._config[table]
        self._enqueue_task(task, delay, now)

    def _enqueue_read_instructions_task(self, delay=0.5, now=None):
        task = _ReadInstructionsTask()
        self._enqueue_task(task, delay, now)

    def _enqueue_task(self, task, delay, now=None):
        now = now or time.time()
        heapq.heappush(self._tasks, (now + delay, task))

class _ReadInstructionsTask(object):
    __slots__ = ()

_PushTableRequestTask = collections.namedtuple(
        '_PushTableRequestTask',
        'device table_id')

def start_manager(queues, config):
    """
    Create and start a new table request manager processes.

    :param queues: is a mapping from `Gateway` to `Queue` objects.
    :param config: is a mapping from `(Device,int)` to floats.

    The `queues` parameter holds the input queues for each `Gateway`.  These
    are used to write new requests to.

    The `config` parameter holds the target delay between requests for each
    `Device` and table pairing.

    The `instruction_queue` is a reference to a `Queue` that the newly created
    process will listen to command messages upon.
    """
    instruction_queue = multiprocessing.Queue()
    p = TableRequestManager(queues, config, instruction_queue)
    p.start()
    return p

def _wakeup_at(t):
    "A rough approximation.  Absolute precision is not necessary"
    now = time.time()
    if t > now:
        time.sleep(t - now)

