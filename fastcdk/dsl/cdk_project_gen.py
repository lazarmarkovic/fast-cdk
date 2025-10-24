import os
import shutil
from importlib.resources import as_file
from pathlib import Path
from typing import Union

from fastcdk.dsl.keep_merge import extract_regions, read_text, splice_regions
from fastcdk.dsl.project_file_list import cdk_project_files


class CDKProjectGenerator:
  def __init__(self, base_gen_path):
    self.base_gen_path = base_gen_path


  def _ensure_inside(self, root: Path, path: Path) -> None:
    """Raise if `path` is not inside `root` (after resolving)."""
    if not path.is_relative_to(root):
      raise ValueError(f"refusing to write outside dest_root: {path}")


  def write_text_at_path(self, content: str, file_path: Union[str, Path], dest_root: Union[str, Path]) -> Path:
    """
    Create dirs under `dest_root` following a *relative* `file_path`,
    then atomically write UTF-8 text with LF newlines. Returns absolute path.
    """
    root = Path(dest_root).expanduser().resolve()
    rel = Path(file_path)

    if rel.is_absolute():
      raise ValueError(f"file_path must be relative, got: {rel}")

    dest = (root / rel).resolve()
    self._ensure_inside(root, dest)

    # create directories as needed, preserve existing structure
    dest.parent.mkdir(parents=True, exist_ok=True)

    # atomic write: write to temp then replace
    tmp = dest.with_suffix(dest.suffix + ".tmp~")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
      f.write(content)
      f.flush()
      os.fsync(f.fileno())
    os.replace(tmp, dest)

    return dest


  def copy_resource_preserve_structure(self,resource, dest_root: Union[str, Path], anchor_name: str = "stack_template") -> Path:
        """
        Copy `resource` to `dest_root` preserving its subpath under `anchor_name`.
        - Never deletes folders; only creates missing ones.
        - Overwrites the destination file if it exists.
        Returns the absolute destination path.
        """
        root = Path(dest_root).expanduser().resolve()

        # build the relative path under the anchor (e.g., 'bin/main.ts' or 'bin/auth/main.ts')
        parts = []
        node = resource.parent
        while True:
          if node is None:
            raise ValueError(f"anchor '{anchor_name}' not found in resource path")
          if getattr(node, "name", None) == anchor_name:
            break
          parts.insert(0, node.name)
          node = node.parent

        rel_path = Path(*parts) / resource.name
        dest = (root / rel_path).resolve()
        self._ensure_inside(root, dest)

        # ensure destination directory exists; never remove existing dirs
        dest.parent.mkdir(parents=True, exist_ok=True)

        # copy file (overwrite only the file; keep dirs)
        with as_file(resource) as src_path:
          shutil.copy2(src_path, dest)  # preserves mtime where possible

        return dest
  

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
      #print(resource)
      self.copy_resource_preserve_structure(resource, self.base_gen_path)

    # generate env config and loading system


    # Generate TS constructs code files
    for cn in construct_nodes:
      for t_key, t_val in cn.definition.templates.table.items():
        self.render_with_keeps(cn.rendered_classes[t_key], Path("lib", t_val.gen_path) / t_val.gen_file_name, self.base_gen_path)


    # Generate stack TS code
    stack_node_rendered_class = stack_node.rendered_classes["this"]
    stack_node_tempalte = stack_node.definition.templates.table["this"]
    self.render_with_keeps(stack_node_rendered_class, Path("lib", stack_node_tempalte.gen_path) / stack_node_tempalte.gen_file_name, self.base_gen_path)
    

  def generate_config_stuff(self, tree, exe_env):
    # build_ctx_and_render.py
    from importlib.resources import as_file, files

    from jinja2 import Environment, FileSystemLoader

    ctx = {
      "tree": tree,
      "iface_name": "EnvConfig",
    }

    resource = files("fastcdk.stack_template.config") / "configSchema.j2"
    resource2 = files("fastcdk.stack_template.env-config") / "env.j2"

    with as_file(resource) as tpl_path:
      env = Environment(loader=FileSystemLoader(str(tpl_path.parent)))
      tpl = env.get_template(tpl_path.name)
      out = tpl.render(ctx)
      self.render_with_keeps(out, Path("config") / "configSchema.ts", self.base_gen_path)
      #print(out)

    # this yields a real filesystem path even if the package is zipped
    with as_file(resource2) as tpl_path2:
      env = Environment(loader=FileSystemLoader(str(tpl_path2.parent)))
      tpl = env.get_template(tpl_path2.name)
      out = tpl.render(ctx)
      self.render_with_keeps(out, Path("env-config") / f"{exe_env}.toml", self.base_gen_path)
      #print(out)