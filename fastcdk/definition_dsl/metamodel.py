from importlib.resources import files

from textx import metamodel_from_str


class MetaModel:
  def __init__(self):
    fcdk_def_grammar_path = files("fastcdk.definition_dsl") / "grammar.tx"
    fcdk_def_grammar_text = fcdk_def_grammar_path.read_text()
    self.mm = metamodel_from_str(fcdk_def_grammar_text, skipws=True)
