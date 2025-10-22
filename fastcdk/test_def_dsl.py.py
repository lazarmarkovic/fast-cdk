from importlib.resources import files

from fastcdk.dsl.cdk_project_gen import CDKProjectGenerator
from fastcdk.dsl.graph_semantic_processor import GraphSemanticProcessor
from fastcdk.dsl.metamodel import MetaModel
from fastcdk.dsl.semantic_processors import SemanticProcessors
from fastcdk.dsl.transformer import Transformer
from fastcdk.util.files import get_definitions_from_path

metamodel = MetaModel().mm
semantic_processor = SemanticProcessors()
metamodel.register_obj_processors(semantic_processor.obj_processors)

def_packages = get_definitions_from_path("fastcdk.stack_template.lib")

print("\n--- Parsing definitions ---")
definitions = []
for def_package in def_packages:
  print(f"Parsing definitions from: {def_package}")
  fcdk_def_text = def_package.read_text()
  model = metamodel.model_from_str(fcdk_def_text)
  for d in model.fcdk.definitions:
    d.base_path = def_package.parent
    definitions.append(d)
print("End parsing definitions\n\n")


#####
print("\n--- Parsing instances ---")
instances = []
#dsl_path = files("fastcdk.dsl_examples") / "network_ex.fcdk"
dsl_path = files("fastcdk.dsl_examples") / "s3based_cf_ex.fcdk"
full_resolved_path = dsl_path.resolve()
print("Full path: " + str(full_resolved_path))
fcdk_text = full_resolved_path.read_text()
model = metamodel.model_from_str(fcdk_text)
for i in model.fcdk.instances:
  i.base_path = full_resolved_path.parent
  instances.append(i)

print("End parsing instances\n\n")


print("Number of instances: " + str(len(instances)))
for i in instances:
  gsp = GraphSemanticProcessor(definitions, i.semantic_data.stack_instance, i.semantic_data.other_instances)
  gsp.add_definitions()
  gsp.add_instances()
  # gsp.visualize()

  transformer = Transformer(gsp.graph)
  nodes, stack_node, exe_env = transformer.transform_nodes()
  tree = transformer.transform_env_vars(nodes)
  print("\n--- End processing instance ---\n\n")


cdkProjectGenerator = CDKProjectGenerator()
cdkProjectGenerator.generate(nodes, stack_node)
cdkProjectGenerator.generate_config_stuff(tree, exe_env)

