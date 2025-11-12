from textx import language

from fastcdk.dsl.metamodel import MetaModel
from fastcdk.dsl.semantic_processors import SemanticProcessors


@language("fastcdk", ["*.fcdk", "*.fcdk_def"])
def fastcdk_language():
  metamodel = MetaModel().mm
  sp = SemanticProcessors()
  metamodel.register_obj_processors(sp.obj_processors)

  return metamodel
