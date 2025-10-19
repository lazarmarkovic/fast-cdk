import json
from dataclasses import is_dataclass, asdict
from types import SimpleNamespace
from collections.abc import Mapping, Iterable

_PRIMS = (str, int, float, bool, type(None))

def _safe_key(k, _seen):
    # keep primitives as-is; stringify everything else
    if isinstance(k, _PRIMS):
        return k
    try:
        hash(k)  # if it's hashable, still stringify for readability
    except Exception:
        pass
    # use repr to avoid creating nested dicts as keys
    return repr(k)

def to_plain(o, _seen=None):
    if _seen is None:
        _seen = set()
    oid = id(o)

    # cycle: embed one shallow preview
    if oid in _seen:
        if hasattr(o, "__dict__"):
            d = {k: v for k, v in vars(o).items()
                 if not k.startswith("_") and not callable(v)}
            # shallow only; stringify values to avoid deep recursion on cycle
            return {"__cycle__": {k: repr(v) for k, v in d.items()}}
        if isinstance(o, Mapping):
            return {"__cycle__": { _safe_key(k, _seen): repr(v) for k, v in o.items() }}
        return {"__cycle__": repr(o)}

    _seen.add(oid)

    # primitives
    if isinstance(o, _PRIMS):
        return o

    # dataclasses
    if is_dataclass(o):
        return to_plain(asdict(o), _seen)

    # SimpleNamespace
    if isinstance(o, SimpleNamespace):
        return to_plain(vars(o), _seen)

    # dict-like (only recurse values; keys → safe strings)
    if isinstance(o, Mapping):
        out = {}
        for k, v in o.items():
            out[_safe_key(k, _seen)] = to_plain(v, _seen)
        return out

    # iterable (not str/bytes)
    if isinstance(o, Iterable) and not isinstance(o, (str, bytes, bytearray)):
        return [to_plain(x, _seen) for x in o]

    # generic object via __dict__
    try:
        d = {k: v for k, v in vars(o).items()
             if not k.startswith("_") and not callable(v)}
        return to_plain(d, _seen)
    except TypeError:
        # slots/C-ext/etc.
        return repr(o)

# usage
# plain = to_plain(this_context)
# print(json.dumps(plain, indent=2, default=str))
