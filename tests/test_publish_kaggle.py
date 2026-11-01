"""The Kaggle upload against a local server that speaks the resumable upload protocol."""
import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

try:
    from kaggle.api import kaggle_api_extended as kae
    from kaggle.api.kaggle_api_extended import ApiStartBlobUploadResponse
except (ImportError, OSError, ValueError, SystemExit):
    pytest.skip("needs the kaggle package and credentials", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("publish_kaggle", ROOT / "scripts" / "publish_kaggle.py")
publish_kaggle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish_kaggle)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self):
        super().__init__(("127.0.0.1", 0), Handler)
        self.blobs: dict[str, bytes] = {}  # what arrived for each upload
        self.sizes: dict[str, int] = {}
        self.first_bytes: list[tuple[str, int]] = []  # where each body started
        self.cut_after: dict[str, int] = {}  # drop the connection after this many bytes, once


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_PUT(self):
        name, srv = self.path.lstrip("/"), self.server
        content_range = self.headers.get("Content-Range", "")
        have = srv.blobs.setdefault(name, b"")
        if content_range.startswith("bytes */"):  # how far did we get?
            if len(have) == srv.sizes[name]:
                return self._reply(200)
            self.send_response(308)
            if have:
                self.send_header("Range", f"bytes=0-{len(have) - 1}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        length = int(self.headers["Content-Length"])
        start = int(content_range.split()[1].split("-")[0]) if content_range else 0  # no range: from the start
        srv.first_bytes.append((name, start))
        limit = srv.cut_after.pop(name, None)
        got = self.rfile.read(limit if limit is not None else length)
        srv.blobs[name] = have[:start] + got
        if limit is not None:
            self.close_connection = True
            self.connection.close()
            return
        self._reply(200)

    def _reply(self, code):
        self.send_response(code)
        self.send_header("Content-Length", "0")
        self.end_headers()


class FakeClient:
    def __init__(self, server, versions):
        def start(request):
            server.sizes[request.name] = request.content_length
            return ApiStartBlobUploadResponse.from_dict(
                {"createUrl": f"http://127.0.0.1:{server.server_port}/{request.name}", "token": "token-" + request.name}
            )

        def create(request):
            versions.append(sorted(f.token for f in request.body.files))
            return SimpleNamespace(status="ok", error="", url="https://kaggle.test/ds")

        self.blobs = SimpleNamespace(blob_api_client=SimpleNamespace(start_blob_upload=start))
        self.datasets = SimpleNamespace(dataset_api_client=SimpleNamespace(create_dataset_version=create))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def setup(tmp_path, monkeypatch):
    server = Server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    versions: list[list[str]] = []
    monkeypatch.setattr(kae.KaggleApi, "authenticate", lambda self: setattr(self, "config_values", {"username": "me"}))
    monkeypatch.setattr(kae.KaggleApi, "build_kaggle_client", lambda self: FakeClient(server, versions))
    monkeypatch.setattr(publish_kaggle, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(kae, "TqdmBufferedReader", kae.TqdmBufferedReader)  # put back afterwards
    monkeypatch.setattr(kae, "Retry", kae.Retry)
    monkeypatch.setattr(publish_kaggle.tempfile, "tempdir", publish_kaggle.tempfile.tempdir)
    folder = tmp_path / "data"
    folder.mkdir()
    (folder / publish_kaggle.METADATA).write_text(json.dumps({"id": "me/ds", "subtitle": "x" * 30, "resources": []}))
    (folder / publish_kaggle.COVER).write_bytes(b"not uploaded")
    (folder / "a.csv").write_bytes(b"a" * 300_000)
    (folder / "b.csv").write_bytes(b"b" * 500_000)
    yield SimpleNamespace(server=server, versions=versions, folder=folder)
    server.shutdown()


def test_uploads_everything_but_the_metadata_and_cover(setup):
    assert publish_kaggle.publish(setup.folder, "notes").status == "ok"
    assert set(setup.server.blobs) == {"a.csv", "b.csv"}
    assert setup.server.blobs["b.csv"] == b"b" * 500_000
    assert setup.versions == [["token-a.csv", "token-b.csv"]]


def test_a_lost_connection_continues_from_the_last_byte(setup):
    setup.server.cut_after["b.csv"] = 200_000
    publish_kaggle.publish(setup.folder, "notes", wait=0)
    assert setup.server.blobs["b.csv"] == b"b" * 500_000
    assert [start for name, start in setup.server.first_bytes if name == "b.csv"] == [0, 200_000]  # not sent again from 0
    assert len(setup.versions) == 1


def test_a_new_run_continues_after_an_interruption(setup, monkeypatch):
    """Ctrl-C part way through b.csv, then the same command again: nothing is sent twice."""
    setup.server.cut_after["b.csv"] = 200_000
    real = kae.KaggleApi.upload_complete
    stop = {"b.csv": True}

    def interrupted(self, path, url, quiet, resume=False):
        result = real(self, path, url, quiet, resume=resume)
        if stop.pop(Path(path).name, False):
            raise KeyboardInterrupt
        return result

    monkeypatch.setattr(kae.KaggleApi, "upload_complete", interrupted)
    reader, http_retry = kae.TqdmBufferedReader, kae.Retry
    with pytest.raises(KeyboardInterrupt):
        publish_kaggle.publish(setup.folder, "notes", wait=0)
    assert setup.versions == []  # no half-uploaded version on Kaggle
    assert len(setup.server.blobs["b.csv"]) == 200_000

    kae.TqdmBufferedReader, kae.Retry = reader, http_retry  # as a new process would find them
    publish_kaggle.publish(setup.folder, "notes", wait=0)
    assert [start for name, start in setup.server.first_bytes if name == "b.csv"] == [0, 200_000]
    assert [start for name, start in setup.server.first_bytes if name == "a.csv"] == [0]  # a finished file is not sent again
    assert setup.server.blobs["a.csv"] == b"a" * 300_000 and setup.server.blobs["b.csv"] == b"b" * 500_000
    assert setup.versions == [["token-a.csv", "token-b.csv"]]


def test_the_resume_state_survives_outside_tmp(setup):
    publish_kaggle.publish(setup.folder, "notes")
    assert publish_kaggle.tempfile.gettempdir() == str(publish_kaggle.STATE_DIR)
