from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# marker regexes (single-line begin/end)

KEEP_BEGIN = re.compile(r"^[ \t]*// fastcdk:keep-start id=(?P<id>[^\s>]+) sig=(?P<sig>[^\s>]+)$", re.M)
KEEP_END = re.compile(r"^[ \t]*// fastcdk:keep-end$", re.M)

@dataclass
class Region:
  id: str
  sig: str
  body: str


@dataclass
class MergeResult:
  text: str
  had_conflict: bool


def extract_regions(text: str | None) -> dict[str, Region]:
  """return id->Region from an existing file (first occurrence wins)."""
  if not text:
    return {}
  regions: dict[str, Region] = {}
  i = 0
  while True:
    mb = KEEP_BEGIN.search(text, i)
    if not mb:
      break
    rid = mb.group("id")
    rsig = mb.group("sig")
    start_body = mb.end()
    me = KEEP_END.search(text, start_body)
    if not me:
      # malformed: stop to avoid runaway capture
      break
    body = text[start_body:me.start()]
    if rid not in regions:
      regions[rid] = Region(rid, rsig, body)
    i = me.end()
  return regions


def splice_regions(fresh_text: str, old_regions: dict[str, Region]) -> MergeResult:
  """
  for each keep block:
    - if (old exists) and (sig matches) -> write old.body, skip fresh inner stub
    - if (old exists) and (sig differs) -> write conflict blob, skip stub
    - if (no old)                       -> keep fresh inner stub (first gen)
  """
  out: list[str] = []
  i = 0
  had_conflict = False

  while True:
    mb = KEEP_BEGIN.search(fresh_text, i)
    if not mb:
      out.append(fresh_text[i:])
      break

    # write up to and including the begin line
    out.append(fresh_text[i:mb.end()])
    rid = mb.group("id")
    new_sig = mb.group("sig")

    me = KEEP_END.search(fresh_text, mb.end())
    if not me:
      # malformed fresh template; write rest and stop
      out.append(fresh_text[mb.end():])
      break

    inner_start, inner_end = mb.end(), me.start()
    fresh_inner = fresh_text[inner_start:inner_end]

    body_to_write = fresh_inner  # default: keep template stub (first generation)
    old = old_regions.get(rid)
    if old is not None:
      if old.sig == new_sig:
        body_to_write = old.body  # exact reuse; DO NOT append fresh stub
      else:
        old.sig = new_sig
        had_conflict = True
        body_to_write = (
            "\n/* >>> fastcdk:CONFLICT (signature changed)\n"
            "old user code:\n--------------------------------\n"
            f"{old.body}"
            "--------------------------------\n"
            "update this region to the new template context (version bumped)\n*/\n"
        )

    out.append(body_to_write)
    # append the closing marker only (no fresh inner again)
    out.append(fresh_text[me.start():me.end()])
    i = me.end()

  return MergeResult("".join(out), had_conflict)



def read_text(path: Path) -> str | None:
  try:
    return path.read_text(encoding="utf-8")
  except FileNotFoundError:
    return None
