from importlib.abc import Traversable
from importlib.resources import files
from pathlib import Path

from textx import metamodel_from_str


class CustomBaseObj:
  def get_dict(self):
    d = dict()
    for name, value in vars(self).items():
      if not name.startswith("_"):
        d[name] = "" if value == "null" else value
    return d


class InputObject(CustomBaseObj):
  def __init__(self):
    super().__init__()

  def add_input(self, input_name, input_value):
    setattr(self, input_name, input_value)


class StackInstanceInputs(CustomBaseObj):
  def __init__(self, assigned_name, def_name, iobj):
    super().__init__()
    self.assigned_name = assigned_name
    self.def_name = def_name
    self.inputs = iobj
    self.children = []

  def add_child(self, name):
    self.children.append(name)


class OtherInstanceInputs(CustomBaseObj):
  def __init__(self, assigned_name, def_name, iobj):
    super().__init__()
    self.assigned_name = assigned_name
    self.def_name = def_name
    self.inputs = iobj


class ModelParser:
  def __init__(self, fcdk_path: Path | Traversable):
    self.fcdk_path = None
    self.metamodel = None
    self.model = None

    self.load_fcdk(fcdk_path)
  
  def kind(self, x): return x.__class__.__name__


  def load_fcdk_metamodel(self) -> None:
    fcdk_grammar_path = files("fastcdk.grammars") / "fcdk_grammar.tx"
    fcdk_grammar_text = fcdk_grammar_path.read_text()
    self.metamodel = metamodel_from_str(fcdk_grammar_text, skipws=True)


  def load_text_file(self, fcdk_path: Path | Traversable) -> None:
    self.fcdk_path = fcdk_path
    fcdk_text = fcdk_path.read_text()
    self.model = self.metamodel.model_from_str(fcdk_text)
    print(f"Loaded FCDK file: {fcdk_path}")

    self.instances = []
    for i in self.model.instances:
      if self.kind(i) == "StackInstance":
        iobj = InputObject()
        iobj.add_input("aws_account_id", i.aws_account_id.val)
        iobj.add_input("aws_region", i.aws_region.val)
        iobj.add_input("aws_stack_name", i.aws_stack_name.val)
        iobj.add_input("project", i.project.val)
        iobj.add_input("exe_env", i.exe_env.val)
        ni = StackInstanceInputs(i.assigned_name, "stack", iobj)
        for c in i.children:
          ni.add_child(c.name)
        self.instances.append(ni)
      else:
        iobj = InputObject()
        for input in i.inputs:
          iobj.add_input(input.key, input.val)
        ni = OtherInstanceInputs(i.assigned_name, i.def_name, iobj)
        self.instances.append(ni)


    print("\n\nInstances:")
    for i in self.instances:
      print(self.kind(i))
      d = i.get_dict()
      for inp in d:
        print(inp, d[inp])
    
    print("\n\n")
