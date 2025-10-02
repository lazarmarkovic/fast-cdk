from importlib.resources import files
from pathlib import Path


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


def get_definitions_from_path(package_name):
  cdk_project_files = list_files_by_depth(package_name)
  def_packages = []
  
  for resource, rel in cdk_project_files:
    extension = Path(resource.name).suffix
    if extension == ".fcdk_def":
      print(f"{rel} {resource.name} (extension: {extension})")
      def_packages.append(rel / resource)

  return def_packages