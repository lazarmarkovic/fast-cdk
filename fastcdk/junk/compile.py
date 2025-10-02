from importlib.resources import files
from pathlib import Path

from fastcdk.fcdk_def import FcdkDef
from fastcdk.fcdk_def_semantics import FcdkDefSemantics
from fastcdk.junk.graph_viz import InteractiveDAG


def list_files_by_depth(package_name):
  root = files(package_name)
  collected: list[tuple[object, int, Path]] = []

  def walk(node, rel_path: Path, depth: int):
    for child in node.iterdir():
      if child.is_dir():
        # descend, accumulating relative sub‑path
        walk(child, rel_path / child.name, depth + 1)
      elif child.is_file():
        # record (Traversable, depth, relative Path)
        collected.append((child, depth, rel_path / child.name))

  # start with empty relative path at depth=0
  walk(root, Path(), 0)

  # sort by folder‑depth, then unzip
  collected.sort(key=lambda tup: tup[1])
  return [(res, rel) for res, _, rel in collected]


cdk_project_files = list_files_by_depth("fastcdk.stack_template.lib")


# # example usage:
defs = []
for resource, rel in cdk_project_files:
  extension = Path(resource.name).suffix

  if extension == ".fcdk_def" and resource.name != "stack.fcdk_def":
    print(f"{rel} {resource.name} (extension: {extension})")
    fcdk_def1 = FcdkDef(rel / resource)
    defs.append(fcdk_def1)

print("\n\nSemantics")
sem = FcdkDefSemantics(defs)
sem.make_global_dep_graph()
print("\n\n")

nodes = sem.global_dep_graph.get_nodes()
edges = sem.global_dep_graph.get_edges()

print("EDGES:")
for e in edges:
  print(e)

# Create and visualize DAG
dag = InteractiveDAG(nodes=nodes, edges=edges)
dag.show()