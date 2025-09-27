from importlib.abc import Traversable
from importlib.resources import files
from pathlib import Path

from jinja2 import StrictUndefined, Template
from textx import metamodel_from_str


class InputObject:
  def __init__(self):
    pass

  def add_input(self, input_name, input_value):
    setattr(self, input_name, input_value)

  def get_dict(self):
    d = dict()
    for name, value in vars(self).items():
      if not name.startswith("_"):
        d[name] = "" if value == "null" else value
    return d

  def is_empty(self):
    return not any(value for value in vars(self).values() if not value.startswith("_"))


class DefaultInputsSection(InputObject):
  def __init__(self, id_prefix, name_prefix, class_prefix, class_name):
    super().__init__()
    self.id_prefix = id_prefix
    self.name_prefix = name_prefix
    self.class_prefix = class_prefix
    self.class_name = class_name


class DepEntry:
  def __init__(self, def_name, assigned_name=None):
    self.def_name = def_name
    self.assigned_name = assigned_name if assigned_name is not None else def_name
    self.input = InputObject()


class EnvVarsEntry:
  def __init__(self, name, config_var, value):
    super().__init__()
    self.name = name
    self.config_var = config_var
    self.value = value


class FcdkDef:
  def __init__(self, fcdk_def_path: Path | Traversable):
    self.load_def(fcdk_def_path)


  def load_def(self, fcdk_def_path: Path | Traversable) -> None:
    fcdk_def_grammar_path = files("fastcdk.grammars") / "fcdk_def_grammar.tx"
    fcdk_def_grammar_text = fcdk_def_grammar_path.read_text()

    fcdk_def_mm = metamodel_from_str(fcdk_def_grammar_text, skipws=True)

    self.fcdk_def_path = fcdk_def_path
    fcdk_def_text = fcdk_def_path.read_text()
    self.model = fcdk_def_mm.model_from_str(fcdk_def_text)

    print("Loading model: " + self.model.name + "\n")
    self.name = self.model.name
    self.template_file = self.model.template_file.val
    self.default_path = self.model.default_path.val
    self.deps = []
    self.env_vars = []
    self.default_inputs = DefaultInputsSection(
      self.model.default_inputs.id_prefix.val,
      self.model.default_inputs.name_prefix.val,
      self.model.default_inputs.class_prefix.val,
      self.model.default_inputs.class_name.val,
    )

    for input_assign in self.model.default_inputs.inputs:
      input_name = input_assign.key
      input_value = input_assign.val
      self.default_inputs.add_input(input_name, input_value)

    self.load_deps()
    self.load_env_vars()

    # if self.deps.__len__() > 0:
    #   print(f"Loaded Deps: {self.deps[0].def_name}")
    # if self.env_vars.__len__() > 0:
    #   print(f"Loaded Env Vars: {self.env_vars[0].name} = {".".join(self.env_vars[0].config_var.parts)} = {self.env_vars[0].value}")


  def load_deps(self):
    if self.model.deps is not None:
      for dep in self.model.deps.entries:
        print(f"Loading Dep: dep_name:{dep.type} ass_name:{dep.key}")
        #print(f"Dep Name: {dep.key if hasattr(dep, 'key') else dep.type}")
        dep_entry = DepEntry(dep.type, dep.key) if dep.key != "" else DepEntry(dep.type)
        #print("Result:" + dep_entry.def_name + " " + dep_entry.assigned_name)
        if hasattr(dep, "props"):
          for inp in dep.props:
            dep_entry.input.add_input(inp.key, inp.val)
          self.deps.append(dep_entry)


  def load_env_vars(self):
    if self.model.env_vars is not None:
      for env_var in self.model.env_vars.entries:
        env_var_entry = EnvVarsEntry(env_var.key, env_var.ref, env_var.val)
        self.env_vars.append(env_var_entry)


  def make_render_dict(self, is_constructor: bool = False) -> dict:
    return {
      "is_class_def": not is_constructor,
      "is_constr_def": is_constructor,
      "name": self.name,
      "template_file": self.template_file,
      "default_path": self.default_path,
      **self.default_inputs.get_dict(),
    }


  def generate_code_from_template(self, is_constructor: bool = False) -> str:
    template_path = self.fcdk_def_path.parent / self.template_file
    template_text = template_path.read_text()
    template = Template(template_text, undefined=StrictUndefined)
    return template.render(self.make_render_dict(is_constructor))

