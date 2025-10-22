import os
import shutil
from importlib.resources import as_file
from pathlib import Path
from typing import Union

from fastcdk.dsl.keep_merge import extract_regions, read_text, splice_regions
from fastcdk.dsl.project_file_list import cdk_project_files


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
    dest_path.write_text(content, encoding="utf-8", newline="\n")
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
  

  def render_with_keeps(self, content: str, file_path: Union[str, Path], dest_root: Union[str, Path]) -> Path:
    dest_root = Path(dest_root).expanduser().resolve()
    rel_path = Path(file_path)
    out_path = (dest_root / rel_path).resolve()

    old_regions = []
    try:
      old_text = read_text(out_path)
      old_regions = extract_regions(old_text)
    except:
      pass

    merged = splice_regions(content, old_regions)
    self.write_text_at_path(merged.text, file_path, dest_root)
    return out_path
  


  def generate(self, construct_nodes, stack_node):
    # Generate basic proejct files
    for resource in cdk_project_files:
      print(resource)

      testing_ground_path = Path("~/code/fast_cdk/testing_ground")
      self.copy_resource_preserve_structure(resource, testing_ground_path)

    # generate env config and loading system


    # Generate TS constructs code files
    for cn in construct_nodes:
      for t_key, t_val in cn.definition.templates.table.items():
        self.render_with_keeps(cn.rendered_classes[t_key], Path("lib", t_val.gen_path) / t_val.gen_file_name, testing_ground_path)


    # Generate stack TS code
    stack_node_rendered_class = stack_node.rendered_classes["this"]
    stack_node_tempalte = stack_node.definition.templates.table["this"]
    self.render_with_keeps(stack_node_rendered_class, Path("lib", stack_node_tempalte.gen_path) / stack_node_tempalte.gen_file_name, testing_ground_path)
    

  def generate_config_stuff(self, tree, exe_env):
    # build_ctx_and_render.py
    from importlib.resources import as_file, files

    from jinja2 import Environment, FileSystemLoader

    ctx = {
      "tree": tree,
      "iface_name": "EnvConfig",
    }

    testing_ground_path = Path("~/code/fast_cdk/testing_ground")
    resource = files("fastcdk.stack_template.config") / "configSchema.j2"
    resource2 = files("fastcdk.stack_template.env-config") / "env.j2"

    with as_file(resource) as tpl_path:
      env = Environment(loader=FileSystemLoader(str(tpl_path.parent)))
      tpl = env.get_template(tpl_path.name)
      out = tpl.render(ctx)
      self.render_with_keeps(out, Path("config") / "configSchema.ts", testing_ground_path)
      print(out)

    # this yields a real filesystem path even if the package is zipped
    with as_file(resource2) as tpl_path2:
      env = Environment(loader=FileSystemLoader(str(tpl_path2.parent)))
      tpl = env.get_template(tpl_path2.name)
      out = tpl.render(ctx)
      self.render_with_keeps(out, Path("env-config") / f"{exe_env}.toml", testing_ground_path)
      print(out)