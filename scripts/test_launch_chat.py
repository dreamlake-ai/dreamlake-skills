"""Exercise the real helper against an isolated Unix WebSocket fixture."""
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import struct
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location(
    'launch_chat', Path(__file__).resolve().parents[1] / 'launch-codex-chat/scripts/launch_chat.py')
launch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch)


@unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'Requires Unix sockets')
class LaunchTests(unittest.TestCase):
    def run_case(self, *, fail=False, full=True, explicit_full=False, check=False, listed=True):
        with tempfile.TemporaryDirectory() as tmp:
            socket_path = tmp + '/server.sock'
            server = socket.socket(socket.AF_UNIX)
            server.bind(socket_path)
            server.listen(1)
            server.settimeout(5)
            calls, errors = [], []

            def serve():
                try:
                    conn, _ = server.accept()
                    conn.settimeout(5)
                    with conn:
                        data = b''
                        while b'\r\n\r\n' not in data:
                            chunk = conn.recv(4096)
                            if not chunk:
                                raise EOFError('Client closed during handshake')
                            data += chunk
                        headers = dict(line.split(b': ', 1) for line in data.split(b'\r\n')[1:] if b': ' in line)
                        accept = base64.b64encode(hashlib.sha1(
                            headers[b'Sec-WebSocket-Key'] + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
                        conn.sendall(b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n'
                                     b'Connection: Upgrade\r\nSec-WebSocket-Accept: ' + accept + b'\r\n\r\n')

                        def exact(n):
                            out = b''
                            while len(out) < n:
                                chunk = conn.recv(n - len(out))
                                if not chunk:
                                    raise EOFError()
                                out += chunk
                            return out

                        def frame(payload, first=129):
                            n = len(payload)
                            header = bytes([first, n]) if n < 126 else bytes([first, 126]) + struct.pack('!H', n)
                            conn.sendall(header + payload)

                        def send(value):
                            payload = json.dumps(value).encode()
                            middle = len(payload) // 2
                            frame(payload[:middle], 1)
                            frame(b'ping', 137)
                            frame(payload[middle:], 128)

                        name = 'test'
                        while True:
                            try:
                                first, second = exact(2)
                            except EOFError:
                                break
                            n = second & 127
                            if n == 126:
                                n = struct.unpack('!H', exact(2))[0]
                            elif n == 127:
                                n = struct.unpack('!Q', exact(8))[0]
                            if not second & 128:
                                raise AssertionError('Client frames must be masked')
                            mask = exact(4)
                            payload = bytes(v ^ mask[i % 4] for i, v in enumerate(exact(n)))
                            if first & 15 == 10:
                                continue
                            request = json.loads(payload)
                            method, params = request['method'], request.get('params', {})
                            calls.append((method, params))
                            if 'id' not in request:
                                continue
                            if method == 'initialize':
                                result = {}
                            elif method == 'thread/start':
                                result = {'thread': {'id': 'test-thread'},
                                          'approvalPolicy': 'never' if full else 'on-request',
                                          'sandbox': {'type': 'dangerFullAccess' if full else 'workspaceWrite'}}
                            elif method == 'thread/name/set':
                                name = params['name']
                                result = {}
                            elif method == 'turn/start':
                                # A fast completion can arrive before the RPC response.
                                send({'method': 'turn/completed', 'params': {
                                    'threadId': 'test-thread', 'turn': {
                                        'id': 'turn-1', 'status': 'failed' if fail else 'completed'}}})
                                result = {'turn': {'id': 'turn-1'}}
                            elif method == 'thread/list':
                                result = {'data': [{'id': 'test-thread', 'name': name, 'cwd': tmp}]
                                          if listed else [], 'nextCursor': None}
                            else:
                                raise AssertionError(method)
                            send({'id': request['id'], 'result': result})
                except Exception as error:
                    errors.append(error)
                finally:
                    server.close()

            worker = threading.Thread(target=serve, daemon=True)
            worker.start()
            output = io.StringIO()
            argv = ['launch_chat.py', '--cwd', tmp, '--name', 'Test chat']
            if explicit_full:
                argv.append('--full-access')
            elif not full:
                argv.append('--host-permissions')
            if check:
                argv.append('--check')
            daemon = {'status': 'running', 'socketPath': socket_path, 'appServerVersion': 'test'}
            with mock.patch.object(sys, 'argv', argv), mock.patch.object(
                    launch.subprocess, 'run', return_value=types.SimpleNamespace(stdout=json.dumps(daemon))), \
                    contextlib.redirect_stdout(output):
                code = launch.main()
            worker.join(6)
            self.assertFalse(worker.is_alive())
            self.assertEqual(errors, [])
            return code, [json.loads(line) for line in output.getvalue().splitlines()], calls

    def test_launch_defaults_to_full_access_and_is_listed(self):
        code, records, calls = self.run_case()
        self.assertEqual(code, 0)
        self.assertEqual(records[-1]['status'], 'ready')
        start = [params for method, params in calls if method == 'thread/start']
        self.assertEqual(len(start), 1)
        self.assertFalse(start[0]['ephemeral'])
        self.assertEqual(start[0]['sandbox'], 'danger-full-access')
        self.assertEqual(start[0]['approvalPolicy'], 'never')

    def test_host_permissions_can_be_requested(self):
        code, _, calls = self.run_case(full=False)
        self.assertEqual(code, 0)
        start = next(params for method, params in calls if method == 'thread/start')
        self.assertNotIn('sandbox', start)
        self.assertNotIn('approvalPolicy', start)

    def test_explicit_full_access(self):
        code, _, calls = self.run_case(explicit_full=True)
        self.assertEqual(code, 0)
        start = next(params for method, params in calls if method == 'thread/start')
        self.assertEqual(start['sandbox'], 'danger-full-access')
        self.assertEqual(start['approvalPolicy'], 'never')

    def test_check_never_creates_a_chat(self):
        code, records, calls = self.run_case(check=True)
        self.assertEqual(code, 0)
        self.assertFalse(records[-1]['createdChat'])
        self.assertEqual([method for method, _ in calls], ['initialize', 'initialized', 'thread/list'])

    def test_failed_greeting_keeps_receipt_without_retry(self):
        code, records, calls = self.run_case(fail=True)
        self.assertEqual(code, 1)
        self.assertEqual(records[-1]['threadId'], 'test-thread')
        self.assertIn('duplicate', records[-1]['nextAction'])
        self.assertEqual(sum(method == 'thread/start' for method, _ in calls), 1)

    def test_missing_list_entry_is_not_success(self):
        code, records, _ = self.run_case(listed=False)
        self.assertEqual(code, 1)
        self.assertEqual(records[-1]['status'], 'error')
        self.assertEqual(records[-1]['threadId'], 'test-thread')


if __name__ == '__main__':
    unittest.main()
