#!/usr/bin/env python3
"""Local preview server for the generated pages, with browser auto-reload.

Serves a directory tree over HTTP and injects a small polling script into
every HTML response: the browser asks ``/__livereload`` twice a second and
reloads itself when the fingerprint (path, size, mtime) of the tree changes.
Standard library only. The server never needs restarting for changed
content -- every request is served from disk and the reload signal comes
from a watcher thread.

Typical use:

    mise run serve                     # http://localhost:8000/
    python3 tools/serve.py --port 9000

Starting it again kills the previous listener on the port first, so the
same command doubles as a restart.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from urllib.parse import unquote, urlsplit

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POLL_INTERVAL = 0.5  # seconds between tree walks in the watcher
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}

RELOAD_SCRIPT = (
    b"<script>"
    b"(function(){var known=null;setInterval(function(){"
    b'fetch("/__livereload",{cache:"no-store"})'
    b".then(function(r){return r.text()})"
    b".then(function(v){"
    b"if(known===null){known=v}else if(v!==known){location.reload()}})"
    b".catch(function(){});},500);})();"
    b"</script>"
)

# The currently served fingerprint; updated by the watcher thread.
state = {"version": ""}


def fingerprint(root):
    """A hash over every served file's path, size and mtime."""
    h = hashlib.sha1()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in sorted(filenames):
            p = os.path.join(dirpath, name)
            try:
                st = os.stat(p)
            except OSError:
                continue
            h.update(p.encode("utf-8", "surrogateescape"))
            h.update(str(st.st_mtime_ns).encode())
            h.update(str(st.st_size).encode())
    return h.hexdigest()


def watch(root):
    """Keep ``state`` current; one changed file flips the version."""
    last = fingerprint(root)
    state["version"] = last
    while True:
        time.sleep(POLL_INTERVAL)
        try:
            now = fingerprint(root)
        except OSError:
            continue
        if now != last:
            last = now
            state["version"] = now


def kill_port(port):
    """Kill whatever still listens on ``port`` from an earlier run."""
    if shutil.which("fuser"):
        subprocess.run(
            ["fuser", "-k", f"{port}/tcp"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    elif shutil.which("lsof"):
        subprocess.run(
            ["sh", "-c", f"lsof -ti tcp:{port} | xargs -r kill"],
            check=False,
        )


def wait_port_free(port, timeout=2.0):
    """Wait until the port can be bound again (kill takes a moment)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return True
            except OSError:
                time.sleep(0.1)
    return False


def inject_reload(html):
    """Insert the polling script before ``</body>`` (append if absent)."""
    if RELOAD_SCRIPT in html:
        return html
    i = html.rfind(b"</body>")
    if i == -1:
        return html + RELOAD_SCRIPT
    return html[:i] + RELOAD_SCRIPT + html[i:]


class ReloadHandler(http.server.SimpleHTTPRequestHandler):
    """Serves files, injecting the reload script into HTML responses."""

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/__livereload":
            self._send_bytes(state["version"].encode(), "text/plain; charset=utf-8")
            return
        body = self._html_with_reload(path)
        if body is not None:
            self._send_bytes(body, "text/html; charset=utf-8")
            return
        super().do_GET()

    def _send_bytes(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _html_with_reload(self, path):
        if not (path.endswith("/") or path.endswith(".html")):
            return None
        fs = self.translate_path(unquote(path))
        if path.endswith("/"):
            fs = os.path.join(fs, "index.html")
        if not os.path.isfile(fs):
            return None
        try:
            with open(fs, "rb") as f:
                data = f.read()
        except OSError:
            return None
        return inject_reload(data)

    def log_request(self, code="-", size="-"):
        if urlsplit(self.path).path == "/__livereload":
            return  # two polls a second would flood the log
        super().log_request(code, size)


def main(argv=None):
    p = argparse.ArgumentParser(description="Serve the pages with browser auto-reload.")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument(
        "--root",
        default=REPO_ROOT,
        help="directory to serve (default: the repository root)",
    )
    args = p.parse_args(argv)
    root = os.path.abspath(args.root)

    kill_port(args.port)
    if not wait_port_free(args.port):
        sys.exit(f"port {args.port} is still busy")

    state["version"] = fingerprint(root)
    threading.Thread(target=watch, args=(root,), daemon=True).start()

    handler = functools.partial(ReloadHandler, directory=root)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(
        f"Serving {root} at http://localhost:{args.port}/ (auto-reload on, Ctrl-C stops)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
