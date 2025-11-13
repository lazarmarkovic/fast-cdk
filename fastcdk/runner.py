from importlib.resources import files
from pathlib import Path
from typing import List, Dict, Any
from fastcdk.dsl.cdk_project_gen import CDKProjectGenerator
from fastcdk.dsl.graph_semantic_processor import GraphSemanticProcessor
from fastcdk.dsl.metamodel import MetaModel
from fastcdk.dsl.semantic_processors import SemanticProcessors
from fastcdk.dsl.transformer import Transformer
from fastcdk.util.files import get_definitions_from_package, get_definitions_from_path



def run(instance_files=None, custom_defs_dirs=None, out_dir=None, make_graph=False):
  metamodel = MetaModel().mm
  semantic_processor = SemanticProcessors()
  metamodel.register_obj_processors(semantic_processor.obj_processors)

  def_packages = get_definitions_from_package("fastcdk.stack_template.lib")


  ######### DEFINITION LOADING

  definitions = []
  print("####### START: Parsing Definitions")
  for def_package in def_packages:
    print(f"Parsing definitions from: {def_package}")
    model = metamodel.model_from_file(def_package)
    for d in model.fcdk.definitions:
      d.base_path = def_package.parent
      definitions.append(d)
  print("####### END: Parsing Definitions---\n\n")



  def_file_paths = []
  for custom_defs_dir in custom_defs_dirs:
    def_file_paths.extend(get_definitions_from_path(custom_defs_dir))
  print("####### START: Parsing Custom Definitions")
  for def_file_path in def_file_paths:
    print(f"Parsing definitions from: {def_file_path}")
    model = metamodel.model_from_file(def_file_path)
    for d in model.fcdk.definitions:
      d.base_path = def_file_path.parent
      definitions.append(d)
  print("####### END: Parsing Custom Definitions---\n\n")


  ######### INSTANCE LOADING

  instances = []
  print("####### START: Parsing Instances")
  for instance_file_path in instance_files:
    print("Parsing instances from: " + str(instance_file_path))
    model = metamodel.model_from_file(instance_file_path)

    inst = model.fcdk.semantic_data 
    inst.base_path = instance_file_path.parent
    instances.append(inst)
  print("####### END: Parsing Instances\n\n")


  print("Number of instances: " + str(len(instances)) + "\n\n")
  for i in instances:
    print(f"####### START: Add Instance {i.stack_instance.stack_name}")
    gsp = GraphSemanticProcessor(definitions, i.stack_instance, i.other_instances)
    gsp.add_definitions()
    gsp.add_instances()

    if make_graph:
      gsp.visualize()

    transformer = Transformer(gsp.graph)
    nodes, stack_node, exe_env = transformer.transform_nodes()
    tree = transformer.transform_env_vars(nodes)
    print(f"####### END: Added Instance {i.stack_instance.stack_name}\n\n")

  testing_ground_path = out_dir
  gen = CDKProjectGenerator(testing_ground_path)
  gen.generate(nodes, stack_node)
  gen.generate_config_stuff(tree, exe_env)