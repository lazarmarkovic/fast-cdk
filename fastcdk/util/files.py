from importlib.resources import files
from pathlib import Path


def list_files_by_depth_package(package_name):
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


def get_definitions_from_package(package_name):
  cdk_project_files = list_files_by_depth_package(package_name)
  def_packages = []
  
  for resource, rel in cdk_project_files:
    extension = Path(resource.name).suffix
    if extension == ".fcdk_def":
      #print(f"{rel} {resource.name} (extension: {extension})")
      def_packages.append(rel / resource)

  return def_packages




def list_files_by_depth_path(root_dir: Path):
    root_dir = Path(root_dir).resolve()
    if not root_dir.is_dir():
        raise NotADirectoryError(f"{root_dir} is not a directory")

    collected: list[tuple[Path, int, Path]] = []

    def walk(abs_node: Path, rel_path: Path, depth: int) -> None:
        for child in abs_node.iterdir():
            if child.is_dir():
                walk(child, rel_path / child.name, depth + 1)
            elif child.is_file():
                collected.append((child, depth, rel_path / child.name))

    walk(root_dir, Path(), 0)
    collected.sort(key=lambda tup: tup[1])  # sort by depth
    return [(abs_path, rel) for abs_path, _, rel in collected]


def get_definitions_from_path(dir_path: Path):
    def_paths = []
    for abs_path, _rel in list_files_by_depth_path(dir_path):
        if abs_path.suffix == ".fcdk_def":
            def_paths.append(abs_path)
    return def_paths