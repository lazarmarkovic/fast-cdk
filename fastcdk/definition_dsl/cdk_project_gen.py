import os
import shutil
from importlib.resources import as_file, files
from pathlib import Path
from typing import Union

from fastcdk.definition_dsl.project_file_list import cdk_project_files


class CDKProjectGenerator:
  def __init__(self):
    pass

  def write_text_at_path(self, content: str, file_path: Union[str, Path], dest_root: Union[str, Path]) -> Path:
    """
    Create directories inside dest_root following file_path, then write `content` to that file.
    `file_path` must be a *relative* path like 'bin/main.ts' or 'bin/auth/main.ts'.
    Returns the absolute destination path.
    """
    dest_root = Path(dest_root).expanduser().resolve()
    rel_path = Path(file_path)

    if rel_path.is_absolute():
        raise ValueError(f"file_path must be relative, got: {rel_path}")

    dest_path = (dest_root / rel_path).resolve()

    # prevent '..' escape outside dest_root
    if not str(dest_path).startswith(str(dest_root) + str(os.sep)):
        raise ValueError(f"refusing to write outside dest_root: {dest_path}")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")
    return dest_path


  def copy_resource_preserve_structure(self, resource, dest_root):
    dest_root = Path(dest_root).expanduser()
    # build the sub‑path under “stack_template”
    parts = []
    node = resource.parent
    while node.name != "stack_template":
      parts.insert(0, node.name)
      node = node.parent
    rel_path = Path(*parts) / resource.name  # e.g. bin/main.ts or bin/auth/main.ts

    # ensure destination directory exists
    dest_path = dest_root / rel_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # copy the actual file
    with as_file(resource) as real_path:
      shutil.copy(real_path, dest_path)

    return dest_path


  def generate(self, construct_nodes, stack_node):
    for resource in cdk_project_files:
      print(resource)
      print("\n\n")

      testing_ground_path = Path("~/code/fast_cdk/testing_ground")
      self.copy_resource_preserve_structure(resource, testing_ground_path)