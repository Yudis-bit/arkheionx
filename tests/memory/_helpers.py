from __future__ import annotations

import contextlib
import io
import tempfile

from arkheionx.cli.main import main


def run_memory_add(*args: str):
    temp = tempfile.TemporaryDirectory()
    argv = ["memory", "add", "--memory-dir", temp.name, "--no-write", *args]
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = main(argv)
    return temp, code, output.getvalue()
