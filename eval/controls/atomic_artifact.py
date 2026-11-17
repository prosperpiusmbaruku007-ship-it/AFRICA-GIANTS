# -*- coding: utf-8 -*-
"""ATOMIC ARTIFACT WRITES for the live harnesses (founder's decision 2026-11-17, after a full-suite run died with a pytest INTERNALERROR while a harness was rewriting its artifact in the background; the cause was never
reproduced, and the hazard on the WRITER's side is real whatever the cause: `json.dump(art, open(OUT, "w"))` TRUNCATES the file first and a reader, a crash, a dropped connection or a Ctrl-C then sees a half-written file).

    write_json(path, obj, **dumps_kwargs)   serialise FIRST (a serialisation error never touches the file), write a sibling temp file, flush + fsync, then os.replace (atomic on one volume): a reader sees the OLD complete
                                            file or the NEW complete file, never a prefix. A failed write removes its temp file and leaves the old artifact untouched.

Windows can refuse os.replace while a reader holds the destination open (PermissionError), so the replace is retried briefly rather than failing a measurement run.
"""
import json
import os
import time


def write_text(path, text, retries=40, delay=0.05):
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        for attempt in range(retries):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if attempt == retries - 1:
                    raise
                time.sleep(delay)
    except BaseException:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        raise


def write_json(path, obj, **dumps_kwargs):
    dumps_kwargs.setdefault("ensure_ascii", False)
    write_text(path, json.dumps(obj, **dumps_kwargs))
