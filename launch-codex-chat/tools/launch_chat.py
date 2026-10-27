#!/usr/bin/env python3
"""Create a persistent chat on an existing Codex WebSocket Unix daemon."""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import time


MAX_MESSAGE = 16 * 1024 * 1024


class Client:
    def __init__(self, path):
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.settimeout(15)
        self.buffer = b""
        self.seq = 0
        self.events = []
        try:
            self.sock.connect(path)
            key = base64.b64encode(os.urandom(16)).decode()
            self.sock.sendall((
                "GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n"
                "Connection: Upgrade\r\nSec-WebSocket-Key: " + key +
                "\r\nSec-WebSocket-Version: 13\r\n\r\n"
            ).encode())
            deadline = time.monotonic() + 15
            while b"\r\n\r\n" not in self.buffer:
                if len(self.buffer) > 16384:
                    raise RuntimeError("Oversized WebSocket handshake")
                self._read(deadline)
            header, self.buffer = self.buffer.split(b"\r\n\r\n", 1)
            lines = header.decode("ascii").split("\r\n")
            headers = {k.lower(): v.strip() for k, v in
                       (line.split(":", 1) for line in lines[1:] if ":" in line)}
            expected = base64.b64encode(hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
            ).digest()).decode()
            if (lines[0].split()[1] != "101" or
                    headers.get("sec-websocket-accept") != expected):
                raise RuntimeError("Daemon did not accept the WebSocket handshake")
            self.call("initialize", {"clientInfo": {
                "name": "launch_codex_chat_skill", "version": "1.0"
            }})
            self.send({"method": "initialized", "params": {}})
        except BaseException:
            self.close()
            raise

    def close(self):
        self.sock.close()

    def _read(self, deadline):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Daemon response deadline exceeded")
        self.sock.settimeout(remaining)
        chunk = self.sock.recv(65536)
        if not chunk:
            raise ConnectionError("Daemon closed the connection")
        self.buffer += chunk

    def exact(self, size, deadline):
        if time.monotonic() >= deadline:
            raise TimeoutError("Daemon response deadline exceeded")
        while len(self.buffer) < size:
            self._read(deadline)
        data, self.buffer = self.buffer[:size], self.buffer[size:]
        return data

    def frame(self, payload, opcode=1):
        size = len(payload)
        if size > MAX_MESSAGE:
            raise ValueError("Message too large")
        if size < 126:
            header = bytes([128 | opcode, 128 | size])
        elif size < 65536:
            header = bytes([128 | opcode, 254]) + struct.pack("!H", size)
        else:
            header = bytes([128 | opcode, 255]) + struct.pack("!Q", size)
        mask = os.urandom(4)
        self.sock.settimeout(15)
        self.sock.sendall(header + mask + bytes(
            value ^ mask[i % 4] for i, value in enumerate(payload)
        ))

    def send(self, message):
        self.frame(json.dumps(message).encode())

    def receive(self, deadline):
        chunks = bytearray()
        while True:
            first, second = self.exact(2, deadline)
            if first & 112:
                raise RuntimeError("Unsupported WebSocket extension")
            size = second & 127
            if size == 126:
                size = struct.unpack("!H", self.exact(2, deadline))[0]
            elif size == 127:
                size = struct.unpack("!Q", self.exact(8, deadline))[0]
            if size + len(chunks) > MAX_MESSAGE:
                raise RuntimeError("Daemon message too large")
            if second & 128:
                raise RuntimeError("Unexpected masked server frame")
            payload = self.exact(size, deadline)
            opcode = first & 15
            if opcode == 8:
                raise ConnectionError("Daemon closed the WebSocket")
            if opcode == 9:
                self.frame(payload, 10)
                continue
            if opcode == 10:
                continue
            if opcode not in (0, 1, 2):
                raise RuntimeError("Unsupported WebSocket opcode")
            chunks.extend(payload)
            if first & 128:
                return json.loads(chunks)

    def call(self, method, params):
        self.seq += 1
        wanted = self.seq
        self.send({"id": wanted, "method": method, "params": params})
        deadline = time.monotonic() + 30
        while True:
            message = self.receive(deadline)
            if message.get("id") == wanted and "method" not in message:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]
            self.handle_event(message)

    def handle_event(self, message):
        if "id" in message and "method" in message:
            self.send({"id": message["id"], "error": {
                "code": -32601, "message": "Launch helper cannot handle this request"
            }})
            raise RuntimeError("Daemon requires an interactive client: " + message["method"])
        if message.get("method") == "turn/completed":
            self.events.append(message["params"])

    def wait_for_turn(self, thread_id, turn_id, timeout):
        deadline = time.monotonic() + timeout
        while True:
            for event in self.events:
                if event.get("threadId") == thread_id and event["turn"]["id"] == turn_id:
                    if event["turn"]["status"] != "completed":
                        raise RuntimeError("Greeting did not complete: " + json.dumps(event["turn"]))
                    return
            self.handle_event(self.receive(deadline))


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only connection check")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--name", default="Remote workspace")
    permissions = parser.add_mutually_exclusive_group()
    permissions.add_argument("--full-access", dest="full_access", action="store_true",
                             help="Maximum permissions (default)")
    permissions.add_argument("--host-permissions", dest="full_access", action="store_false",
                             help="Keep the host's permission defaults")
    parser.set_defaults(full_access=True)
    parser.add_argument("--timeout", type=float, default=120, help="Greeting deadline in seconds")
    args = parser.parse_args()
    if not args.name.strip() or args.timeout <= 0:
        parser.error("Name must be nonempty and timeout must be positive")
    cwd = args.cwd.resolve()
    if not args.check and not cwd.is_dir():
        parser.error("Working directory does not exist")
    client = None
    thread_id = None
    try:
        process = subprocess.run(
            ["codex", "app-server", "daemon", "version"],
            check=True, capture_output=True, text=True, timeout=20
        )
        daemon = json.loads(process.stdout)
        if daemon.get("status") != "running" or not daemon.get("socketPath"):
            raise RuntimeError("No running daemon with a local socket; inspect codex remote-control start")
        client = Client(daemon["socketPath"])
        if args.check:
            client.call("thread/list", {"limit": 1})
            emit({"status": "connected", "version": daemon.get("appServerVersion"),
                  "threadListReadable": True, "createdChat": False})
            return 0
        params = {"cwd": str(cwd), "ephemeral": False}
        if args.full_access:
            params.update(approvalPolicy="never", sandbox="danger-full-access")
        result = client.call("thread/start", params)
        thread_id = result["thread"]["id"]
        emit({"status": "created", "threadId": thread_id, "cwd": str(cwd),
              "approvalPolicy": result.get("approvalPolicy"), "sandbox": result.get("sandbox")})
        if args.full_access and (result.get("approvalPolicy") != "never" or
                                result.get("sandbox", {}).get("type") != "dangerFullAccess"):
            raise RuntimeError("Requested full access was not returned by the server")
        title = {"threadId": thread_id, "name": args.name}
        client.call("thread/name/set", title)
        turn = client.call("turn/start", {"threadId": thread_id, "input": [{
            "type": "text", "text": "This chat was created at my request so I can continue "
            "in my connected Codex app. Reply briefly that this workspace session is ready, "
            "then wait for my next message. Do not run tools or change any files."
        }]})
        client.wait_for_turn(thread_id, turn["turn"]["id"], args.timeout)
        client.call("thread/name/set", title)
        cursor = None
        found = None
        for _ in range(10):
            query = {"searchTerm": args.name, "limit": 100}
            if cursor:
                query["cursor"] = cursor
            page = client.call("thread/list", query)
            found = next((thread for thread in page["data"] if thread["id"] == thread_id), None)
            cursor = page.get("nextCursor")
            if found or not cursor:
                break
        if not found:
            raise RuntimeError("Created thread is not present in the interactive thread list")
        emit({"status": "ready", "threadId": thread_id, "name": found.get("name"),
              "cwd": found.get("cwd"), "listed": True, "clientVisibility": "not inspected"})
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError,
            subprocess.SubprocessError) as error:
        emit({"status": "error", "error": str(error), "threadId": thread_id,
              "nextAction": "Inspect this thread before retrying; do not create a duplicate."
              if thread_id else "Inspect the running daemon and installed protocol version."})
        return 1
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    sys.exit(main())
