"""Demo: defensive patterns that the Anchorlaw scanner detects (P1-P6)."""

import os


def swallow_all(path):
    """P1 swallowed exception: except: pass."""
    try:
        with open(path) as f:
            return f.read()
    except:
        pass
    return ""


def broad_catch(data):
    """P2 broad except Exception."""
    try:
        return data["key"] + 1
    except Exception:
        return None


def defensive_null(x):
    """P3 defensive null propagation chain (and no anchor declared)."""
    if x is None:
        return None
    inner = x.get("a")
    if inner is None:
        return None
    deeper = inner.get("b")
    if deeper is None:
        return None
    return deeper


def meaningless_test(a):
    """P4 meaningless test: assert f(x) == f(x)."""
    assert meaningless_test(a) == meaningless_test(a)
    return a


def vague_todo():
    """P6 vague TODO without a tracker number."""
    # TODO: fix this later
    return os.getcwd()
