# -*- coding: utf-8 -*-
"""Shim -> shared/build_engine.py (tek ortak motor, KİLİT 2026-09).

Video-özel mantık burada YOK — hepsi shared/build_engine.py içinde, TEK yerde.
Bir bugfix/özellik artık sadece orada yapılır ve otomatik olarak her videoya
(eskiler dahil) yansır. Eski build_composition.py'nin orijinali git geçmişinde
duruyor — bir şey ters giderse `git checkout -- videos/<id>/build_composition.py`.
"""
import os
import sys
from pathlib import Path

_VIDEO_ROOT = Path(__file__).resolve().parent
_SHARED = _VIDEO_ROOT.parents[1] / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))
os.environ["NIHAT_BUILD_ROOT"] = str(_VIDEO_ROOT)
import build_engine  # noqa: E402,F401 -- import tetikler, module-level build çalışır
