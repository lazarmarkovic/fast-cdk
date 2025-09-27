from importlib.resources import files
from pathlib import Path

from fastcdk.fcdk import Fcdk
from fastcdk.fcdk_def import FcdkDef
from fastcdk.fcdk_def_semantics import FcdkDefSemantics
from fastcdk.graph_viz import InteractiveDAG

# fcdk_def_path = files("fastcdk.stack_template.lib.modules.s3based_cloudfront_frontend.cloudfront") / "cloudfront.s3cf.fcdk_def"

# fcdk_def1 = FcdkDef(fcdk_def_path)
# t_code = fcdk_def1.generate_code_from_template()
# print(t_code)


# Traverse the files("fastcdk.stack_template.lib) to find all the templates and defs
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

  if extension == ".fcdk_def":
    print(f"{rel} {resource.name} (extension: {extension})")
    fcdk_def1 = FcdkDef(rel / resource)
    defs.append(fcdk_def1)

print("\n\nSemantics")
sem = FcdkDefSemantics(defs)
sem.make_global_dep_graph()

#
#
# Add the examples for fcdk
dsl_path = files("fastcdk.fastcdk_dsl_examples") / "network_example.fcdk"
fcdk_loaded = Fcdk(dsl_path)
sem.add_instances(fcdk_loaded.instances)

print("\n\n")

nodes = sem.global_dep_graph.get_nodes()
edges = sem.global_dep_graph.get_edges()

print("EDGES:")
for e in edges:
  print(e)

# Create and visualize DAG
dag = InteractiveDAG(nodes=nodes, edges=edges)
dag.show()


# print("CDK Project File Copy:")


# import shutil
# from importlib.resources import files, as_file

# testing_ground_path = Path("~/code/fast_cdk/testing_ground")


# def copy_resource_preserve_structure(resource, dest_root):
#   dest_root = Path(dest_root).expanduser()

#   # build the sub‑path under “stack_template”
#   parts = []
#   node = resource.parent
#   while node.name != "stack_template":
#     parts.insert(0, node.name)
#     node = node.parent
#   rel_path = Path(*parts) / resource.name  # e.g. bin/main.ts or bin/auth/main.ts

#   # ensure destination directory exists
#   dest_path = dest_root / rel_path
#   dest_path.parent.mkdir(parents=True, exist_ok=True)

#   # copy the actual file
#   with as_file(resource) as real_path:
#     shutil.copy(real_path, dest_path)

#   return dest_path


# for resource in cdk_project_files:
#   print(resource)  # prints the paths of the project files defined in cdk_project_files

#   copy_resource_preserve_structure(resource, testing_ground_path)
