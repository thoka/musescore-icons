"""The dev server: injection, reload endpoint, fingerprint, restart."""

from __future__ import annotations

import functools
import http.server
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.request

import pytest

import serve


@pytest.fixture
def server(tmp_path):
    """A handler on an ephemeral port, serving a throwaway directory."""
    handler = functools.partial(serve.ReloadHandler, directory=str(tmp_path))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    serve.state["version"] = "v-test"
    yield srv
    srv.shutdown()


def get(url):
    with urllib.request.urlopen(url) as r:
        return r.status, r.headers, r.read()


def url(srv, path):
    return f"http://127.0.0.1:{srv.server_address[1]}{path}"


def test_html_gets_reload_script(server, tmp_path):
    (tmp_path / "page.html").write_text("<html><body><p>hi</p></body></html>")
    status, _, body = get(url(server, "/page.html"))
    assert status == 200
    assert body.index(serve.RELOAD_SCRIPT) < body.index(b"</body>")


def test_directory_index_gets_reload_script(server, tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "index.html").write_text("<html><body>x</body></html>")
    status, _, body = get(url(server, "/sub/"))
    assert status == 200
    assert serve.RELOAD_SCRIPT in body


def test_non_html_served_untouched(server, tmp_path):
    (tmp_path / "i.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    status, headers, body = get(url(server, "/i.svg"))
    assert status == 200
    assert serve.RELOAD_SCRIPT not in body
    assert body == '<svg xmlns="http://www.w3.org/2000/svg"/>'.encode()


def test_livereload_endpoint_returns_version(server):
    status, _, body = get(url(server, "/__livereload"))
    assert status == 200
    assert body == b"v-test"


def test_missing_page_falls_through(server):
    with pytest.raises(urllib.error.HTTPError) as e:
        get(url(server, "/nope.html"))
    assert e.value.code == 404


def test_inject_without_body_tag():
    assert serve.inject_reload(b"<p>x</p>") == b"<p>x</p>" + serve.RELOAD_SCRIPT


def test_inject_is_idempotent():
    once = serve.inject_reload(b"<html><body></body></html>")
    assert serve.inject_reload(once) == once


def test_fingerprint_tracks_changes(tmp_path):
    before = serve.fingerprint(str(tmp_path))
    (tmp_path / "new.txt").write_text("x")
    after = serve.fingerprint(str(tmp_path))
    assert before != after


def test_watch_updates_state(tmp_path):
    threading.Thread(target=serve.watch, args=(str(tmp_path),), daemon=True).start()
    deadline = time.monotonic() + 2
    while serve.state["version"] == "v-test" and time.monotonic() < deadline:
        time.sleep(0.02)  # wait for the thread's baseline
    base = serve.state["version"]
    time.sleep(serve.POLL_INTERVAL + 0.05)  # no change yet -> same version
    assert serve.state["version"] == base
    (tmp_path / "f.txt").write_text("x")
    deadline = time.monotonic() + serve.POLL_INTERVAL * 3
    while serve.state["version"] == base and time.monotonic() < deadline:
        time.sleep(0.05)
    assert serve.state["version"] != base


@pytest.mark.skipif(shutil.which("fuser") is None, reason="fuser not installed")
def test_kill_port_frees_the_port(tmp_path):
    port = _held_port()
    proc = subprocess.Popen(
        ["python3", "-c",
         f"import socket,time; s=socket.socket(); s.bind(('127.0.0.1',{port}));"
         "s.listen(); time.sleep(30)"]
    )
    try:
        time.sleep(0.3)  # let the child bind
        serve.kill_port(port)
        assert serve.wait_port_free(port)
        proc.wait(timeout=5)
        assert proc.returncode != 0
    finally:
        proc.kill()


def _held_port():
    with __import__("socket").socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
