"""Sandbox-aware pytest runner for the Anchorlaw repo (DSH Windows sandbox).

Why this exists
---------------
The DSH Windows sandbox seals any directory created with POSIX mode 0o700
(owner-only): the directory becomes inaccessible to every process —
including the creating process itself (listdir / mkdir / rmdir all fail
with WinError 5, and even icacls cannot read the ACL).

pytest's tmp machinery hardcodes mode=0o700 in five places
(_pytest/tmpdir.py: mktemp, getbasetemp; _pytest/pathlib.py:
make_numbered_dir / make_numbered_dir_with_cleanup). Without a workaround,
`tmp_path` fixtures error out and session cleanup crashes, so the
AGENTS.md baseline check (`python -m pytest --rootdir=python
python/tests -q`) cannot run under this sandbox.

Fix
---
Rewrite mode 0o700 -> 0o755 at the os.mkdir level before pytest starts.
os.makedirs and pathlib.Path.mkdir both funnel through os.mkdir, so a
single patch covers every call site. Empirically probed: only exactly
0o700 seals; 0o750 / 0o711 / 0o701 / 0o600 are unaffected.

Additional notes
----------------
* Use a NON-dot-prefixed --basetemp (e.g. tmp-pytest-bt): the scanner
  skips files under hidden (dot) directories, so a dot basetemp makes
  every tmp_path fixture invisible to scan_directory tests.
* The sealed dirs themselves cannot be removed from a sandboxed process;
  delete them with an escalated (danger-full-access) shell if they
  accumulate.

Usage (from repo root)
----------------------
python dsh/scripts/run_tests_sandbox.py --rootdir=python python/tests -q \
    --basetemp=E:\\path\\to\\tmp-pytest-bt
"""

import os
import sys

_orig_mkdir = os.mkdir


def _sandbox_mkdir(path, mode=0o777, *, dir_fd=None):
    if mode == 0o700:
        mode = 0o755
    if dir_fd is not None:
        return _orig_mkdir(path, mode, dir_fd=dir_fd)
    return _orig_mkdir(path, mode)


os.mkdir = _sandbox_mkdir

import pytest

if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv[1:]))
