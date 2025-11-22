from importlib.resources import files

from textx import metamodel_from_file


class MetaModel:
  def __init__(self):
    fcdk_def_grammar_path = files("fastcdk.dsl") / "grammar.tx"
    self.mm = metamodel_from_file(fcdk_def_grammar_path, skipws=True)
