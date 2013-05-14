# -*- coding: utf-8 -*-

"""

"""

import collections
import heapq
import multiprocessing
import Queue
import time

import jem_data.core.domain as domain
import jem_data.core.messages as messages

class TableRequestManager(multiprocessing.Process):

    def __init__(self, queues, config, instructions):
        super(TableRequestManager, self).__init__()
        self._queues = queues.copy()
        self._config = config.copy()
        self._instructions = instructions
        self._tasks = []
        self._sending_requests = False

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

    def start_recording(self, recording):
        '''Resets the current config to only request the given tables.
        '''
        tables = []
        for gateway in recording.gateways:
            gateway_addr = domain.GatewayAddr(gateway.host, gateway.port)
            for device in gateway.devices:
                device_addr = domain.DeviceAddr(gateway_addr, device.unit)
                for table in device.tables:
                    tables.append(domain.TableAddr(device_addr, table.id))

        self._instructions.put(_ResetRequests(tables=tables))

    def stop_requests(self):
        self._instructions.put(_StopRequests())

    def resume_requests(self):
        self._instructions.put(_ResumeRequests())

    def _run_task(self, task):
        if isinstance(task, _PushTableRequestTask):
            self._run_push_table_request_task(task)
        elif isinstance(task, _ReadInstructionsTask):
            self._run_read_instructions_task(task)
        else:
            raise ValueError("Unknown Task Type: %s" % task)

    def _run_push_table_request_task(self, task):
        device, table_id = task.device, task.table_id
        if self._sending_requests:
            print "Making request to %s : %s" % (device, table_id)
            q = self._queues[device.gateway]
            req = messages.ReadTableMsg(
                    device = device,
                    table_id = table_id)
            q.put(req)
        self._enqueue_push_table_request_task((device, table_id))

    def _run_read_instructions_task(self, task):
        try:
            while True:
                instruction = self._instructions.get(block=False)
                self._run_instruction(instruction)
        except Queue.Empty:
            pass
        finally:
            self._enqueue_read_instructions_task()

    def _run_instruction(self, instruction):
        if isinstance(instruction, _StopRequests):
            self._sending_requests = False
        elif isinstance(instruction, _ResumeRequests):
            self._sending_requests = True
        elif isinstance(instruction, _ResetRequests):
            self._run_reset_instruction(instruction)
        else:
            raise ValueError, "Unknown Instruction Type: %s" % instruction

    def _run_reset_instruction(self, instruction):
        gateways = set( device.gateway for (device, _) in instruction.tables )
        for gateway in gateways:
            if gateway not in self._queues:
                raise Exception("Uh oh: no queue for gateway: %s" % (gateway,))

        self._config = dict( (t, 0.5) for t in instruction.tables )
        now = time.time()
        for table in self._config:
            self._enqueue_push_table_request_task(table, now=now)
        self._sending_requests = True

    def _enqueue_push_table_request_task(self, table, now=None):
        task = _PushTableRequestTask(*table)
        if table in self._config:
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

_ResetRequests = collections.namedtuple(
        '_ResetRequests',
        'tables')

class _StopRequests(object):
    __slots__ = ()

class _ResumeRequests(object):
    __slots__ = ()

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

