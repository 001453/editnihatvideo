# -*- coding: utf-8 -*-
"""Yerel dashboard: surukle-birak upload, hazirla, studio ac."""
from __future__ import annotations

import cgi
import json
import os
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
VIDEOS = ROOT / "videos"
INBOX = ROOT / "_inbox"
DASH = ROOT / "dashboard.html"
PORT = 8765
PY = sys.executable

JOBS: dict[str, dict] = {}


def py312():
    try:
        r = subprocess.run(
            ["py", "-3.12", "-c", "import sys; print(sys.executable)"],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return PY


def sanitize_id(raw: str) -> str:
    s = unquote(raw or "").strip()
    s = re.sub(r"\.mp4$", "", s, flags=re.I)
    s = re.sub(r"[^\w\-]+", "", s, flags=re.U)
    return s


def set_job(vid, **kw):
    JOBS.setdefault(vid, {"id": vid, "log": []})
    JOBS[vid].update(kw)
    if "msg" in kw:
        JOBS[vid]["log"].append(kw["msg"])
        JOBS[vid]["log"] = JOBS[vid]["log"][-60:]


def prepare_worker(vid: str, source: str, account: str, force: bool = True):
    set_job(vid, status="running", msg="klasor + encode basliyor (cozunurluk ayni, hizli draft)")
    try:
        src = Path(source)
        if not src.is_file():
            set_job(vid, status="error", msg=f"dosya degil: {source}")
            return
        cmd = [
            py312(), str(SCRIPTS / "prepare_video.py"), vid,
            "--source", str(src),
            "--account", account,
            "--quality", "draft",
        ]
        if force:
            cmd.append("--force")
        set_job(vid, msg=" ".join(cmd))
        r = subprocess.run(
            cmd, cwd=str(ROOT), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        out = (r.stdout or "") + (r.stderr or "")
        for line in out.splitlines():
            set_job(vid, msg=line[:400])
        if r.returncode != 0:
            set_job(vid, status="error", msg=f"hata kodu {r.returncode}")
            return
        prompt = ""
        p = VIDEOS / vid / "PACKAGE_ME.txt"
        if p.exists():
            prompt = p.read_text(encoding="utf-8").strip()
        set_job(vid, status="ready", msg="transcript + altyazi hazir", prompt=prompt)
    except Exception as e:
        set_job(vid, status="error", msg=str(e))


def open_studio(vid: str):
    vid = sanitize_id(vid)
    dest = VIDEOS / vid
    if not dest.exists():
        return False, "klasor yok"
    env = os.environ.copy()
    env["HYPERFRAMES_SKIP_SKILLS"] = "1"
    builder = dest / "build_composition.py"
    if builder.exists() and (dest / "project.json").exists():
        subprocess.run([py312(), str(builder)], cwd=str(dest))
    subprocess.Popen(
        ["npx", "--yes", "hyperframes@0.8.30", "preview"],
        cwd=str(dest),
        env=env,
        shell=True,
    )
    return True, "Studio aciliyor (HyperFrames preview)"


class Handler(BaseHTTPRequestHandler):
    # buyuk video upload
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path: Path, ctype="text/html; charset=utf-8"):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self._cors()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/dashboard", "/dashboard.html"):
            return self._file(DASH)
        if u.path.startswith("/api/status/"):
            vid = sanitize_id(u.path.split("/")[-1])
            return self._json(200, JOBS.get(vid) or {"id": vid, "status": "idle", "log": []})
        if u.path == "/api/videos":
            items = []
            if VIDEOS.exists():
                for d in sorted(VIDEOS.iterdir()):
                    if not d.is_dir() or d.name.startswith("_"):
                        continue
                    items.append({
                        "id": d.name,
                        "has_video": (d / "public" / "input-video.mp4").exists(),
                        "has_project": (d / "project.json").exists(),
                        "package_me": (d / "PACKAGE_ME.txt").exists(),
                    })
            return self._json(200, {"videos": items})
        self._json(404, {"error": "not found"})

    def do_POST(self):
        u = urlparse(self.path)
        ctype = self.headers.get("Content-Type", "")

        if u.path == "/api/upload-prepare" and "multipart/form-data" in ctype:
            return self._upload_prepare()

        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return self._json(400, {"error": "bad json"})

        if u.path == "/api/prepare":
            vid = sanitize_id(data.get("id") or "")
            source = (data.get("source") or "").strip().strip('"')
            account = (data.get("account") or "nihat").strip()
            if not vid:
                return self._json(400, {"error": "Video ID gerekli (orn: 0910)"})
            if not source:
                return self._json(400, {"error": "dosya yolu veya surukle-birak gerekli"})
            src = Path(source)
            if not src.is_file():
                return self._json(400, {"error": f"MP4 dosyasi degil (klasor olamaz): {source}"})
            if JOBS.get(vid, {}).get("status") == "running":
                return self._json(409, {"error": "zaten calisiyor"})
            set_job(vid, status="queued", msg="kuyrukta", prompt="")
            threading.Thread(
                target=prepare_worker, args=(vid, str(src), account, True), daemon=True
            ).start()
            return self._json(200, {"ok": True, "id": vid})

        if u.path == "/api/studio":
            vid = sanitize_id(data.get("id") or "")
            ok, msg = open_studio(vid)
            return self._json(200 if ok else 400, {"ok": ok, "msg": msg})

        self._json(404, {"error": "not found"})

    def _upload_prepare(self):
        try:
            env = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
            }
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=env)
            vid_raw = form.getfirst("id") or ""
            account = (form.getfirst("account") or "nihat").strip()
            vid = sanitize_id(vid_raw)
            if not vid:
                return self._json(400, {"error": "Video ID gerekli (orn: 0910)"})
            fileitem = form["file"] if "file" in form else None
            if fileitem is None or not getattr(fileitem, "file", None):
                return self._json(400, {"error": "video dosyasi yok — surukle veya sec"})
            filename = Path(fileitem.filename or "upload.mp4").name
            if not filename.lower().endswith((".mp4", ".mov", ".m4v", ".webm")):
                return self._json(400, {"error": "sadece video dosyasi (mp4/mov)"})
            INBOX.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"[^\w.\-]+", "_", filename)
            dest = INBOX / f"{vid}__{safe}"
            with open(dest, "wb") as out:
                while True:
                    chunk = fileitem.file.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            if dest.stat().st_size < 1000:
                dest.unlink(missing_ok=True)
                return self._json(400, {"error": "dosya cok kucuk / bozuk"})
            if JOBS.get(vid, {}).get("status") == "running":
                return self._json(409, {"error": "zaten calisiyor"})
            set_job(vid, status="queued", msg=f"yuklendi: {dest.name}", prompt="")
            threading.Thread(
                target=prepare_worker, args=(vid, str(dest), account, True), daemon=True
            ).start()
            return self._json(200, {"ok": True, "id": vid, "saved": str(dest)})
        except Exception as e:
            return self._json(500, {"error": str(e)})


def main():
    if not DASH.exists():
        raise SystemExit(f"dashboard.html yok: {DASH}")
    INBOX.mkdir(parents=True, exist_ok=True)
    # Windows default socket timeout issues with large uploads — bump
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    httpd.request_queue_size = 16
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Dashboard: {url}", flush=True)
    print("Surukle-birak MP4; cozunurluk ayni kalir (hizli draft encode).", flush=True)
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("kapandi")


if __name__ == "__main__":
    main()
