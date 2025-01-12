"""
Dummy Client Script.

This script connects to a Frisbee Server using WebSockets and performs authentication.
It authenticates with the server, receives messages from the server, and sends sample data to the server.
"""


import asyncio
import csv
import inspect
import json
import logging
import os
import random
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

import websockets
from websockets import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK, WebSocketClientProtocol

from frisbee.dev.dummy_clients.ble_hr import run_ble_hr
from frisbee.otree_extension.messages import MessageType, BaseMessage

PARTICIPANT_LABEL = 'Alice'
URL = 'ws://127.0.0.1:8001'
ADMIN_PASSWORD = 'admin'
SEND_RATE: int | None = None  # messages per second (set by command line argument or Frisbee Server)
SAMPLE_RATE_PER_SEND: int | None = None  # number of data points to send in one message (set by command line argument or Frisbee Server)
AUTO_SEND: bool = False
FILE: str | None = None
BLE_HR: bool = False


@dataclass(kw_only=True)
class DataPoint:
    data: str
    time_recorded: str

    def to_json(self) -> str:
        return json.dumps(self, default=lambda obj: obj.__dict__)


def setup_logger() -> logging.Logger:
    module_logger = logging.getLogger(__name__)
    module_logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    c_formatter = logging.Formatter("%(levelname)s: %(message)s")
    c_handler.setFormatter(c_formatter)
    module_logger.addHandler(c_handler)

    return module_logger


logger = setup_logger()

"""
def create_rand_value() -> Iterator[int]:
    while True:
        yield random.randint(0, 100)"""


def create_rand_value() -> Iterator[dict]:
    while True:
        yield {
            # TODO should match structure from the real client in the future
            "heart_rate": random.randint(60, 100),
            "energy_expended": 0,
            "rr_intervals": 0
        }


def read_csv_data(file_path: str) -> Iterator[dict[str, str]]:
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, strict=False)
        try:
            for row in csv_reader:
                yield row
        except csv.Error as e:
            logger.error(f'[CLIENT] Error reading CSV file {file_path}, line {csv_reader.line_num}: {e}')
            raise


async def auth_with_frisbee_server(websocket: WebSocketClientProtocol) -> bool:
    msg_value = {
        # 'admin_username': 'admin',
        'admin_password': ADMIN_PASSWORD,
        'participant_label': PARTICIPANT_LABEL,
    }
    msg = BaseMessage(type=MessageType.AUTH_CREDENTIALS, value=msg_value)

    try:
        await websocket.send(msg.to_json())
        auth_resp = await websocket.recv()
        auth_status = json.loads(auth_resp)
    except ConnectionClosed:
        logger.exception(f"WebSocket connection closed unexpectedly")
        return False
    else:
        if auth_status.get('value', {}).get('status') == 'success':
            logger.info(f'[FRISBEE SERVER] {auth_status}')
            logger.info('[CLIENT] Authentication with Frisbee Server successful')
            return True
        else:
            logger.error(f'[FRISBEE SERVER] {auth_status}')
            logger.error(f'[CLIENT] Authentication with Frisbee Server failed. '
                         f'{auth_status.get("value", {}).get("err_msg")}')
            return False


async def consumer_handler(
        websocket: WebSocketClientProtocol,
        config_ready_event: asyncio.Event,
        send_msg_event: asyncio.Event,
) -> None:
    """Receive messages from the Frisbee Server."""
    async for message in websocket:
        logger.info(f"[FRISBEE SERVER] {message}")

        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            logger.exception("[CLIENT] Received invalid JSON message from Frisbee Server")
            continue

        message_type = message.get("type")

        if message_type == "rec_cmd":
            cmd = message.get("value", {}).get("cmd")

            if cmd == "start":
                send_msg_event.set()
            elif cmd in ["pause", "stop"]:
                send_msg_event.clear()

        elif message_type == "client_config":
            config = message.get("value", {})
            send_rate = config.get("send_rate")
            sample_rate_per_send = config.get("sample_rate_per_send")

            global SEND_RATE, SAMPLE_RATE_PER_SEND
            if SEND_RATE is None:
                SEND_RATE = send_rate
            else:
                logger.info(f"[CLIENT] Overwriting send rate {send_rate} from Frisbee Server "
                            f"with {SEND_RATE} from command line")
            if SAMPLE_RATE_PER_SEND is None:
                SAMPLE_RATE_PER_SEND = sample_rate_per_send
            else:
                logger.info(f"[CLIENT] Overwriting sample rate per send {sample_rate_per_send} from Frisbee Server "
                            f"with {SAMPLE_RATE_PER_SEND} from command line")

            config_ready_event.set()

    else:
        # The iterator above exits normally when the connection is closed with close code 1000 (OK) or
        # 1001 (going away) or without a close code. Otherwise, it raises a ConnectionClosedError.
        # We raise ConnectionClosedOK manually to handle and log normal exit cases els.
        ok, going_away = 1000, 1001
        if websocket.close_code in (ok, going_away):
            exc = ConnectionClosedOK(
                websocket.close_rcvd,
                websocket.close_sent,
                websocket.close_rcvd_then_sent
            )
            raise exc


async def producer_handler(
        websocket: WebSocketClientProtocol,
        config_ready_event: asyncio.Event,
        send_msg_event: asyncio.Event,
        hr_measurement_queue: asyncio.Queue,
) -> None:
    """Send messages to the Frisbee Server."""
    await config_ready_event.wait()
    msg_count = 0
    pause_btw_sends = 1/SEND_RATE
    pause_btw_sample = pause_btw_sends/SAMPLE_RATE_PER_SEND
    if FILE is not None:
        data_generator = read_csv_data(FILE)
    elif BLE_HR:
        async def qgen(q: asyncio.Queue) -> AsyncIterator:
            while True:
                yield await q.get()
        data_generator = qgen(hr_measurement_queue)
    else:
        data_generator = create_rand_value()

    while True:
        if not AUTO_SEND:
            await send_msg_event.wait()
        batch = []
        for _ in range(SAMPLE_RATE_PER_SEND):
            try:
                if inspect.isgenerator(data_generator):
                    data = next(data_generator)
                else:
                    data = await anext(data_generator)
            except csv.Error:
                # only read_csv_data generator can raise csv.Error
                return
            except StopIteration:
                # Only read_csv_data generator can raise StopIteration, create_rand_value is infinite.
                logger.error(f'[CLIENT] File {FILE} has no more data and incomplete batch will not be sent. '
                             f'Shutting down ...')
                return
            except StopAsyncIteration:
                # Only qgen generator can raise StopAsyncIteration.
                logger.error(f'[CLIENT] BLE device has no more data and incomplete batch will not be sent. '
                             f'Shutting down ...')
                return
            data_point = DataPoint(
                data=json.dumps(data),
                time_recorded=datetime.now(timezone.utc).isoformat()
            )
            batch.append(data_point.__dict__)
            await asyncio.sleep(pause_btw_sample)

        msg_value = {
            'data_points': batch,
            'time_sent': datetime.now(timezone.utc).isoformat()
        }
        msg = BaseMessage(type=MessageType.SENSOR_DATA_POINTS, value=msg_value)

        logger.debug(f"[CLIENT] Sending message to Frisbee Server: {msg}. Message #{msg_count}")
        msg_count += 1
        await websocket.send(msg.to_json())


async def handler() -> None:
    config_ready_event = asyncio.Event()
    send_msg_event = asyncio.Event()

    hr_m_queue = None
    if BLE_HR:
        hr_m_task, hr_m_queue = await run_ble_hr(send_msg_event)

    async with websockets.connect(URL) as ws:
        authenticated = await auth_with_frisbee_server(ws)
        if not authenticated:
            return
        consumer_task = asyncio.create_task(consumer_handler(ws, config_ready_event, send_msg_event))
        producer_task = asyncio.create_task(producer_handler(ws, config_ready_event, send_msg_event, hr_m_queue))

        try:
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except asyncio.CancelledError:
            consumer_task.cancel()
            producer_task.cancel()
            await asyncio.gather(consumer_task, producer_task, return_exceptions=True)
            raise

        else:
            for task in pending:
                task.cancel()

            handled_exceptions = []
            for task in done:
                exc = task.exception()
                if exc:
                    # Handle and log exceptions once to prevent log clutter.
                    # E.g. ConnectionClosed exceptions may be raised by both tasks.
                    exc_id = (type(exc), exc.args)
                    if exc_id not in handled_exceptions:
                        handle_exception(exc)
                        handled_exceptions.append(exc_id)


def handle_exception(exc: BaseException) -> None:
    if isinstance(exc, (ConnectionClosedError, ConnectionClosedOK)):
        handle_websocket_exception(exc)
    else:
        logger.error('[CLIENT] Unhandled exception', exc_info=exc)


def handle_websocket_exception(exc: ConnectionClosedOK | ConnectionClosedError) -> None:
    if isinstance(exc, ConnectionClosedOK):
        logger.info(f'[CLIENT] Disconnected from Frisbee Server: {exc}')
    elif isinstance(exc, ConnectionClosedError):
        logger.error(f'[CLIENT] Disconnected from Frisbee Server unexpectedly: {exc}')


def is_file_exists_and_readable(file_path: str) -> bool:
    file_path = Path(file_path)

    if not file_path.is_file():
        logger.error(f'[CLIENT] {file_path} does not exist or is not a file')
        return False

    if not os.access(file_path, os.R_OK):
        logger.error(f'[CLIENT] {file_path} does not have read permissions')
        return False

    return True


def run(**kwargs) -> None:
    global PARTICIPANT_LABEL, URL, ADMIN_PASSWORD, SEND_RATE, SAMPLE_RATE_PER_SEND, AUTO_SEND, FILE, BLE_HR
    PARTICIPANT_LABEL = kwargs['participant-label']
    URL = kwargs['url']
    ADMIN_PASSWORD = kwargs['password']
    SEND_RATE = kwargs['send_rate']
    SAMPLE_RATE_PER_SEND = kwargs['sample_rate_per_send']
    AUTO_SEND = kwargs['auto_send']
    FILE = kwargs['file']
    BLE_HR = kwargs['ble_hr']  # TODO make compatible with AUTO_SEND

    if FILE is not None and BLE_HR:
        logger.error("[CLIENT] Options '--file' and '--ble-hr' cannot be used at the same time.")
        return

    if FILE is not None:
        if not is_file_exists_and_readable(FILE):
            return

    try:
        asyncio.run(handler())
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt received. Shutting down ...')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Frisbee Dummy Client Script')
    help_str = '(default: %(default)s)'
    parser.add_argument('participant-label', default=PARTICIPANT_LABEL, help=help_str, nargs='?')
    parser.add_argument('-s', '--send_rate', type=int, default=SEND_RATE, help=help_str)
    parser.add_argument('-r', '--sample-rate-per-send', type=int, default=SAMPLE_RATE_PER_SEND, help=help_str)
    parser.add_argument('-a', '--auto-send', action='store_true', help=help_str)
    parser.add_argument('-f', '--file', type=str, default=FILE, help=help_str)
    parser.add_argument('-b', '--ble-hr', action='store_true', default=True, help=help_str)  # Changed this line
    parser.add_argument('-u', '--url', default=URL, help=help_str)
    parser.add_argument('-P', '--password', default=ADMIN_PASSWORD, help=help_str)

    args = parser.parse_args()
    run(**vars(args))
