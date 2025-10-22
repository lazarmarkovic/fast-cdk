from collections import defaultdict
from typing import Hashable, Iterable


def reverse_chains_allow_merges(edges: Iterable[tuple[Hashable, Hashable]]):
  next_of: dict[Hashable, Hashable] = {}              # u -> v (no splits)
  prevs: defaultdict[Hashable, set] = defaultdict(set) # v -> {u1,u2,...}
  problems: list[str] = []

  def prob(msg: str): problems.append(msg)

  # degrees + self-loop/split checks
  for u, v in edges:
    if u == v:
      prob(f"{u} -> {v}")
      continue
    if u in next_of and next_of[u] != v:
      prob(f"{u} -> {next_of[u]} and {u} -> {v}")
    else:
      next_of[u] = v
    prevs[v].add(u)

  # collect nodes
  nodes: set[Hashable] = set()
  for u, v in edges:
    nodes.add(u); nodes.add(v)

  # cycle detection (easy with out-degree <= 1)
  visited: set[Hashable] = set()
  onpath: set[Hashable] = set()

  def walk_from(u: Hashable):
    cur = u
    while cur is not None:
      if cur in onpath:
        # reconstruct simple cycle for message
        cyc = [cur]
        x = next_of[cur]
        while x != cur:
          cyc.append(x)
          x = next_of[x]
        cyc.append(cur)
        prob(" -> ".join(map(str, cyc)))
        return
      if cur in visited:
        return
      visited.add(cur)
      onpath.add(cur)
      cur = next_of.get(cur)
    onpath.clear()

  for n in nodes:
    if n not in visited:
      onpath.clear()
      walk_from(n)

  if problems:
    return [], problems

  # enumerate reverse chains from tails; branch on merges
  tails = sorted([n for n in nodes if n not in next_of], key=str)
  chains: list[list[Hashable]] = []

  def backtrack(path: list[Hashable]):
    cur = path[-1]
    preds = sorted(prevs.get(cur, ()), key=str)
    if not preds:
      chains.append(path[:])
      return
    for p in preds:
      backtrack(path + [p])

  for t in tails:
    backtrack([t])

  # deterministic ordering of results
  chains.sort(key=lambda c: tuple(map(str, c)))
  return chains, problems