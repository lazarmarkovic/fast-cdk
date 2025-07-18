from importlib.resources import files
from pathlib import Path

from jinja2 import StrictUndefined, Template
from textx import metamodel_from_str

fcdk_def_grammar_path = files("fastcdk.grammars") / "fcdk_def_grammar.tx"
fcdk_def_grammar_text = fcdk_def_grammar_path.read_text()
fcdk_def_mm = metamodel_from_str(fcdk_def_grammar_text, skipws=True)

fcdk_def_path = files("fastcdk.stack_template.lib.modules.cloudwatch_log") / "log.fcdk_def"
fcdk_def_text = fcdk_def_path.read_text()

program = fcdk_def_mm.model_from_str(fcdk_def_text)

print(program.__dict__.keys())

d = dict()

d[program.name] = {
  "template_file": program.template_file.val,
  "default_path": program.default_path.val,
  "deps": None,
  "env_vars": None,
  "default_inputs": None,
}

d[program.name]["default_inputs"] = {
  "id_prefix": program.default_inputs_section.id_prefix.val,
  "name_prefix": program.default_inputs_section.name_prefix.val,
  "class_prefix": program.default_inputs_section.class_prefix.val,
  "class_name": program.default_inputs_section.class_name.val,
}

fcdk_template_path = files("fastcdk.stack_template.lib.modules.cloudwatch_log") / "log.j2"
fcdk_template_text = fcdk_template_path.read_text()


def make_dot_dict(d):
  class DotDict(dict):
    def __getattr__(self, key):
      val = self.get(key)
      return DotDict(val) if isinstance(val, dict) else val

    def __setattr__(self, key, value):
      self[key] = value

    def __delattr__(self, key):
      del self[key]

  return DotDict(d)


def make_j2_template_constructor(definition):
  pass


def make_j2_template_class(definition, is_constructor=False):
  definition = make_dot_dict(definition)
  data = {
    "is_class_def": not is_constructor,
    "is_constr_def": is_constructor,
    "template_file": definition.template_file,
    "default_path": definition.default_path,
    **d[program.name]["default_inputs"],
  }

  j2_template = Template(fcdk_template_text, undefined=StrictUndefined)
  return j2_template.render(make_dot_dict(data))


# print(make_j2_template_class(d[program.name]))


def list_files_by_depth(package_name: str):
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


# example usage:
for resource, rel in list_files_by_depth("fastcdk.stack_template.lib"):
  print(f"{rel}" + " " + resource.name)  # e.g. Foo.txt, subdir/Bar.py, subdir/nested/Baz.json,
