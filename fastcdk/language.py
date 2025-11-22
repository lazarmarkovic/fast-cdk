from textx import language, metamodel_from_file

from fastcdk.dsl.metamodel import MetaModel
from fastcdk.dsl.semantic_processors import SemanticProcessors

from os.path import dirname, join


@language("fastcdk", "*.fcdk")
def fastcdk_language():
  # metamodel = MetaModel().mm
  # sp = SemanticProcessors()
  # metamodel.register_obj_processors(sp.obj_processors)

  return metamodel_from_file(join(dirname(__file__), "dsl" , "grammar.tx"))
