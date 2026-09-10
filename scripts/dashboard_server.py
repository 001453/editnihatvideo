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
CAPS_PAGE = ROOT / "captions.html"
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


def prepare_worker(vid: str, source: str, account: str, force: bool = False, only: str = "all"):
    set_job(vid, status="running", msg=f"basliyor ({only})")
    try:
        src = Path(source) if source else None
        cmd = [
            py312(), str(SCRIPTS / "prepare_video.py"), vid,
            "--account", account,
            "--quality", "draft",
            "--only", only,
        ]
        if src and src.is_file():
            cmd.extend(["--source", str(src)])
        # force sadece acikca istendiğinde; paket silinmesin
        if force and only == "all":
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
        set_job(vid, status="ready", msg=f"tamam ({only})", prompt=prompt)
    except Exception as e:
        set_job(vid, status="error", msg=str(e))


def rebuild_video(vid: str):
    dest = VIDEOS / vid
    builder = dest / "build_composition.py"
    template = ROOT / "template" / "build_composition.py"
    if not dest.exists():
        return False, "klasor yok"
    if template.exists():
        import shutil
        shutil.copy2(template, builder)
    if not builder.exists():
        return False, "build_composition.py yok"
    r = subprocess.run(
        [py312(), str(builder)], cwd=str(dest),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.returncode != 0:
        return False, (r.stderr or r.stdout or "rebuild hata")[-400:]
    return True, (r.stdout or "rebuild OK").strip().splitlines()[-1] if r.stdout else "rebuild OK"


def fix_tr_captions(vid: str):
    path = VIDEOS / vid / "project.json"
    if not path.exists():
        return False, "project.json yok"
    sys.path.insert(0, str(SCRIPTS))
    from tr_text import caption_display  # noqa: E402
    project = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for c in project.get("captions") or []:
        top = caption_display(c.get("top") or "")
        bot = caption_display(c.get("bottom") or c.get("text") or "")
        if top != (c.get("top") or "") or bot != (c.get("bottom") or ""):
            n += 1
        c["top"] = top
        c["bottom"] = bot
        c["text"] = f"{top} {bot}".strip()
    path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    return True, f"{n} satir duzeltildi / {len(project.get('captions') or [])} altyazi"


def broll_slots(vid: str):
    """timeline.json broll[] + dosya var mi."""
    dest = VIDEOS / vid
    tl_path = dest / "timeline.json"
    slots = []
    if tl_path.exists():
        try:
            tl = json.loads(tl_path.read_text(encoding="utf-8"))
            for i, b in enumerate(tl.get("broll") or []):
                fid = (b.get("id") or f"b{i+1}").strip()
                fname = (b.get("file") or f"broll/{fid}.mp4").replace("\\", "/")
                path = dest / "public" / fname
                slots.append({
                    "index": i + 1,
                    "id": fid,
                    "keyword": (b.get("keyword") or fid).upper(),
                    "start": float(b.get("start") or 0),
                    "dur": 8.0,  # locked — always 8s
                    "file": fname,
                    "ready": path.is_file() and path.stat().st_size > 1000,
                    "hint": b.get("hint") or "",
                })
        except Exception:
            pass
    return slots


def attach_broll(vid: str, slot_id: str, raw_path: Path):
    """Ham videoyu 9:16 b-roll olarak encode edip public/broll/<id>.mp4 yazar."""
    dest = VIDEOS / vid
    if not dest.exists():
        return False, "klasor yok"
    slots = broll_slots(vid)
    hit = None
    for s in slots:
        if s["id"] == slot_id or str(s["index"]) == str(slot_id) or s["keyword"].lower() == str(slot_id).lower():
            hit = s
            break
    if not hit:
        # fallback: slot_id dosya adi
        hit = {"id": sanitize_id(slot_id) or "broll", "file": f"broll/{sanitize_id(slot_id) or 'broll'}.mp4"}
    out = dest / "public" / hit["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(SCRIPTS))
    from encode_input import encode  # noqa: E402
    encode(raw_path, out, broll=True, quality="draft")
    # timeline pending kaldir
    tl_path = dest / "timeline.json"
    if tl_path.exists():
        tl = json.loads(tl_path.read_text(encoding="utf-8"))
        for b in tl.get("broll") or []:
            b["dur"] = 8.0  # locked
        remaining = [s for s in broll_slots(vid) if s["id"] != hit["id"] and not s["ready"]]
        tl["brollPending"] = len(remaining) > 0
        tl_path.write_text(json.dumps(tl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True, f"{hit.get('keyword', hit['id'])} baglandi → {hit['file']} (8s)"


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
        if u.path in ("/captions", "/captions.html"):
            if not CAPS_PAGE.exists():
                return self._json(404, {"error": "captions.html yok"})
            return self._file(CAPS_PAGE)
        if u.path.startswith("/api/status/"):
            vid = sanitize_id(u.path.split("/")[-1])
            return self._json(200, JOBS.get(vid) or {"id": vid, "status": "idle", "log": []})
        if u.path.startswith("/api/project/"):
            vid = sanitize_id(u.path.split("/")[-1])
            path = VIDEOS / vid / "project.json"
            if not path.exists():
                return self._json(404, {"error": f"project.json yok: {vid}"})
            try:
                project = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                return self._json(500, {"error": str(e)})
            return self._json(200, {"id": vid, "project": project})
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
                        "has_captions": False,
                        "package_me": (d / "PACKAGE_ME.txt").exists(),
                        "has_index": (d / "index.html").exists(),
                    })
                    if items[-1]["has_project"]:
                        try:
                            caps = json.loads((d / "project.json").read_text(encoding="utf-8")).get("captions") or []
                            items[-1]["has_captions"] = len(caps) > 0
                            items[-1]["caption_count"] = len(caps)
                        except Exception:
                            pass
            return self._json(200, {"videos": items})
        if u.path.startswith("/api/broll-slots/"):
            vid = sanitize_id(u.path.split("/")[-1])
            if not (VIDEOS / vid).exists():
                return self._json(404, {"error": "klasor yok"})
            slots = broll_slots(vid)
            return self._json(200, {"id": vid, "slots": slots, "ready": all(s["ready"] for s in slots) if slots else False})
        self._json(404, {"error": "not found"})

    def do_POST(self):
        u = urlparse(self.path)
        ctype = self.headers.get("Content-Type", "")

        if u.path == "/api/upload-prepare" and "multipart/form-data" in ctype:
            return self._upload_prepare()
        if u.path == "/api/upload-broll" and "multipart/form-data" in ctype:
            return self._upload_broll()

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
                target=prepare_worker, args=(vid, str(src), account, False), daemon=True
            ).start()
            return self._json(200, {"ok": True, "id": vid})

        if u.path == "/api/studio":
            vid = sanitize_id(data.get("id") or "")
            ok, msg = open_studio(vid)
            return self._json(200 if ok else 400, {"ok": ok, "msg": msg})

        if u.path == "/api/rebuild":
            vid = sanitize_id(data.get("id") or "")
            ok, msg = rebuild_video(vid)
            return self._json(200 if ok else 400, {"ok": ok, "msg": msg})

        if u.path == "/api/fix-tr":
            vid = sanitize_id(data.get("id") or "")
            ok, msg = fix_tr_captions(vid)
            if ok and data.get("rebuild"):
                ok2, msg2 = rebuild_video(vid)
                msg = f"{msg} · {msg2}"
                ok = ok and ok2
            return self._json(200 if ok else 400, {"ok": ok, "msg": msg})

        if u.path == "/api/action":
            # Parçalı hızlı işlem: transcribe | captions | flag | rebuild | fix-tr
            vid = sanitize_id(data.get("id") or "")
            action = (data.get("action") or "").strip()
            account = (data.get("account") or "nihat").strip()
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            if action == "rebuild":
                ok, msg = rebuild_video(vid)
                return self._json(200 if ok else 400, {"ok": ok, "msg": msg})
            if action == "fix-tr":
                ok, msg = fix_tr_captions(vid)
                if ok and data.get("rebuild", True):
                    ok2, msg2 = rebuild_video(vid)
                    msg = f"{msg} · {msg2}"
                    ok = ok and ok2
                return self._json(200 if ok else 400, {"ok": ok, "msg": msg})
            if action in ("transcribe", "captions", "flag"):
                if JOBS.get(vid, {}).get("status") == "running":
                    return self._json(409, {"error": "zaten calisiyor"})
                set_job(vid, status="queued", msg=f"kuyruk: {action}", prompt="")
                threading.Thread(
                    target=prepare_worker, args=(vid, "", account, False, action), daemon=True
                ).start()
                return self._json(200, {"ok": True, "id": vid, "action": action})
            return self._json(400, {"error": f"bilinmeyen action: {action}"})

        if u.path == "/api/captions/save":
            vid = sanitize_id(data.get("id") or "")
            caps = data.get("captions")
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            path = VIDEOS / vid / "project.json"
            if not path.exists():
                return self._json(404, {"error": "project.json yok"})
            if not isinstance(caps, list):
                return self._json(400, {"error": "captions listesi gerekli"})
            try:
                sys.path.insert(0, str(SCRIPTS))
                from tr_text import caption_display  # noqa: E402
                project = json.loads(path.read_text(encoding="utf-8"))
                cleaned = []
                for c in caps:
                    if not isinstance(c, dict):
                        continue
                    top = caption_display(c.get("top") or "")
                    bot = caption_display(c.get("bottom") or c.get("text") or "")
                    item = dict(c)
                    item["top"] = top
                    item["bottom"] = bot
                    item["text"] = (c.get("text") or f"{top} {bot}").strip()
                    item["start"] = float(c.get("start") or 0)
                    item["end"] = float(c.get("end") or 0)
                    cleaned.append(item)
                project["captions"] = cleaned
                path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
                msg = f"{len(cleaned)} altyazı kaydedildi"
                if data.get("rebuild"):
                    ok, rmsg = rebuild_video(vid)
                    if not ok:
                        return self._json(500, {"error": "kaydedildi ama rebuild hata", "log": rmsg})
                    msg += " · rebuild OK — Studio Ctrl+F5"
                return self._json(200, {"ok": True, "msg": msg, "count": len(cleaned)})
            except Exception as e:
                return self._json(500, {"error": str(e)})

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
            # force=False: mevcut paketi silme; bos/yarim klasoru prepare kendisi toparlar
            threading.Thread(
                target=prepare_worker, args=(vid, str(dest), account, False), daemon=True
            ).start()
            return self._json(200, {"ok": True, "id": vid, "saved": str(dest)})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def _upload_broll(self):
        try:
            env = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
            }
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=env)
            vid = sanitize_id(form.getfirst("id") or "")
            slot = (form.getfirst("slot") or form.getfirst("keyword") or "").strip()
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            if not slot:
                return self._json(400, {"error": "slot/keyword gerekli (vakif veya getiri)"})
            fileitem = form["file"] if "file" in form else None
            if fileitem is None or not getattr(fileitem, "file", None):
                return self._json(400, {"error": "b-roll videosu yok"})
            filename = Path(fileitem.filename or "broll.mp4").name
            if not filename.lower().endswith((".mp4", ".mov", ".m4v", ".webm")):
                return self._json(400, {"error": "sadece video (mp4/mov)"})
            INBOX.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"[^\w.\-]+", "_", filename)
            raw = INBOX / f"{vid}__broll_{sanitize_id(slot)}__{safe}"
            with open(raw, "wb") as out:
                while True:
                    chunk = fileitem.file.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            if raw.stat().st_size < 1000:
                raw.unlink(missing_ok=True)
                return self._json(400, {"error": "dosya cok kucuk"})
            ok, msg = attach_broll(vid, slot, raw)
            if not ok:
                return self._json(400, {"error": msg})
            rebuilt = None
            if (form.getfirst("rebuild") or "").strip() in ("1", "true", "yes"):
                ok2, msg2 = rebuild_video(vid)
                rebuilt = msg2
                if not ok2:
                    return self._json(200, {"ok": True, "msg": msg, "rebuild_error": msg2})
            slots = broll_slots(vid)
            return self._json(200, {
                "ok": True,
                "msg": msg,
                "rebuild": rebuilt,
                "slots": slots,
                "ready": all(s["ready"] for s in slots) if slots else False,
            })
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
