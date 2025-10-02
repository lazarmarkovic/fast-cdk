
from textx import get_location
from textx.exceptions import TextXSemanticError

from fastcdk.data_structure.errors import NodeAlreadyExistsError
from fastcdk.data_structure.graph import GraphNode, NodeNotFoundError, NodeType
from fastcdk.definition_dsl.class_model import DefaultInputsSem, DefSem, DepSem, DepsSem, EnvVarSem, EnvVarsSem, OtherInstanceSem, OtherInstancesSem, StackInstanceSem, InstancesSem
from fastcdk.definition_dsl.class_model import deep_copy_def

class SemanticProcessors:
  def __init__(self, graph):
    self.graph = graph

    self.definitions = []
    self.obj_processors = {
      'EnvVar': self.env_var,
      'EnvVarsSection': self.env_vars_section,
      'DefaultInputsSection': self.default_inputs_section,
      'DepEntry': self.dep_entry,
      'DepsSection': self.deps_section,
      'Definition': self.definition,

      'Instance': self.instance,
      'OtherInstances': self.other_instance,
      'StackInstance': self.stack_instance,
    }


  ###### OBJECT PROCESSING ######
  def _join_ref_parts(self, ref) -> list[str]:
    return [ref.first, *list(ref.rest)]
  

  def env_var(self, entity):
    parts = self._join_ref_parts(entity.ref)
    entity.semantic_data = EnvVarSem(
      name=entity.key,
      path_joined=".".join(parts),
      path_parts=tuple(parts),
      value=entity.val,
    )


  def env_vars_section(self, entity):
    entity.semantic_data = EnvVarsSem(
      table={ev.semantic_data.name: ev.semantic_data for ev in entity.entries}
    )


  def default_inputs_section(self, entity):
    extras = {}
    for i in entity.inputs:
      if i.key in {"id_prefix","name_prefix","class_prefix","class_name"} or i.key in extras:
        raise TextXSemanticError(f"Duplicate input variable '{i.key}' in default_inputs.", **get_location(i.key))
      extras[i.key] = i.val

    entity.semantic_data = DefaultInputsSem(
      id_prefix=entity.id_prefix.val,
      name_prefix=entity.name_prefix.val,
      class_prefix=entity.class_prefix.val,
      class_name=entity.class_name.val,
      extras=extras,
    )


  def dep_entry(self, entity):
    if (entity.assigned_name == entity.def_name):
      raise TextXSemanticError(f"Dep entry assigned_name '{entity.assigned_name}' cannot be the same as definition name.", **get_location(entity))
    if (entity.assigned_name == entity.source_assigned_name or entity.def_name == entity.source_assigned_name):
      raise TextXSemanticError(f"Dep entry source_assigned_name '{entity.source_assigned_name}' cannot be the same as assigned name or definition name.", **get_location(entity)) 
  
    props_dict = {}
    for i in entity.props:
      if (i.key in props_dict):
        raise TextXSemanticError(f"Duplicate input variable '{i.key}' in dep_entry section.", **get_location(i))
      if getattr(i, "ref", None) is not None:
        parts = self._join_ref_parts(i.ref)
        props_dict[i.key] = EnvVarSem(
          name=i.key,
          path_joined=".".join(parts),
          path_parts=tuple(parts),
          value=None,
        )
      else:
        props_dict[i.key] = i.val
  
    entity.semantic_data = DepSem(
      assigned_name=entity.assigned_name,
      def_name=entity.def_name if entity.def_name != '' else entity.assigned_name,
      source_assigned_name=entity.source_assigned_name,
      props=props_dict
    )


  def deps_section(self, entity):
    table = {}
    for dep in entity.entries:
      k = dep.semantic_data.assigned_name
      if k in table:
        raise TextXSemanticError(f"Duplicate dep assigned name '{k}' in deps section.", **get_location(dep))
      table[k] = dep.semantic_data
    entity.semantic_data = DepsSem(table=table)


  def definition(self, entity):
    deps = getattr(entity.deps, "semantic_data", None) or DepsSem({})
    envs = getattr(entity.env_vars, "semantic_data", None) or EnvVarsSem({})
    default_inputs = getattr(entity.default_inputs, "semantic_data", None) or DefaultInputsSem({})

    entity.semantic_data = DefSem(
      name=entity.name,
      template_file=entity.template_file.val,
      default_path=entity.default_path.val,
      deps=deps,
      env_vars=envs,
      default_inputs=default_inputs,
    )
  

  #########################
  ##### Instance processors
  def other_instance(self, entity):
    if (entity.assigned_name == entity.def_name):
      raise TextXSemanticError(f"Dep entry assigned_name '{entity.assigned_name}' cannot be the same as definition name.", **get_location(entity))

    inputs_dict = {}
    for i in entity.inputs:
      if (i.key in inputs_dict):
        raise TextXSemanticError(f"Duplicate input variable '{i.key}' in dep_entry section.", **get_location(i))
      if getattr(i, "ref", None) is not None:
        parts = self._join_ref_parts(i.ref)
        inputs_dict[i.key] = EnvVarSem(
          name=i.key,
          path_joined=".".join(parts),
          path_parts=tuple(parts),
          value=None,
        )
      else:
        inputs_dict[i.key] = i.val
  
    entity.semantic_data = OtherInstanceSem(
      assigned_name=entity.assigned_name,
      def_name=entity.def_name if entity.def_name != '' else entity.assigned_name,
      inputs=inputs_dict,
      dep_overrides=tuple([depo.name for depo in entity.dep_overrides])
    )


  def stack_instance(self, entity):
    entity.semantic_data = StackInstanceSem(
      stack_name=entity.stack_name,
      aws_account_id=entity.aws_account_id.val,
      aws_region=entity.aws_region.val,
      aws_stack_name=entity.aws_stack_name.val,
      project=entity.project.val,
      exe_env=entity.exe_env.val,
      children=tuple(c.name for c in entity.children)
    )


  def instance(self, entity):
    stack_instance = getattr(entity.stack_instance, "semantic_data", None) or StackInstanceSem({})
    
    other_instances_table = {}
    for oi in entity.other_instances:
      k = oi.semantic_data.assigned_name
      if k in other_instances_table:
        raise TextXSemanticError(f"Duplicate instance name '{k}' in instance section.", **get_location(oi))
      other_instances_table[k] = oi.semantic_data

    entity.semantic_data = InstancesSem(
      stack_instance=stack_instance,
      other_instances=OtherInstancesSem(table=other_instances_table)
    )



  ###### MODEL PROCESSING ######
  def model_processor(self, model, metamodel):
    print("Add Definitions")
    definitions = getattr(model.fcdk, "definitions", None) or []
    instances = getattr(model.fcdk, "instances", None) or []

    for definition in definitions:
      print("Definition name: " + definition.semantic_data.name)

      try:
        new_node = GraphNode(definition.semantic_data, NodeType.DEFINITION)
        self.graph.add_node(new_node)
      except NodeAlreadyExistsError as err:
        raise TextXSemanticError(f"Definition with name '{definition.semantic_data.name}' already exists.", **get_location(definition)) from err
    print("Definition(s) processed\n")
      

    print("\n\n")
    print("Add Instances")
    for instance in instances:
      print("Instance name: " + instance.semantic_data.stack_instance.stack_name)

      # Find all dep override indicators
      dep_overrides = set()
      for oi in instance.semantic_data.other_instances.table:
        oi_obj = instance.semantic_data.other_instances.table[oi]
        for dov in oi_obj.dep_overrides:
          dep_overrides.add(dov)
          print("-------" + dov)

      # Check if all dep overrides exist in instances
      for dep in dep_overrides:
        if dep not in instance.semantic_data.other_instances.table:
          raise TextXSemanticError(f"Dep override '{dep}' not found among instances.", **get_location(instance))
        

      for oi_key in [*instance.semantic_data.stack_instance.children, *dep_overrides]:
        if oi_key not in instance.semantic_data.other_instances.table:
          raise TextXSemanticError(f"Stack child '{oi_key}' not defined.", **get_location(instance))
        
        oi = instance.semantic_data.other_instances.table[oi_key]

         # Find required definition to be used
        node_to_copy = self.graph.get_node(oi.def_name)
        if node_to_copy is None:
          raise TextXSemanticError(f"Definition for instance named '{oi_key}' not found.", **get_location(instance))
        
        # Make deep copy of definition
        def_deep_copy = deep_copy_def(node_to_copy.definition)
        oi.apply_to(def_deep_copy)

        # Make new node with deeo copy
        new_node = GraphNode(def_deep_copy, NodeType.INSTANCE, assigned_name=oi.assigned_name, edges=node_to_copy.edges)
        self.graph.add_node(new_node)
      try:
        new_node = GraphNode(definition.semantic_data, NodeType.INSTANCE)
        self.graph.add_node(new_node)
      except NodeAlreadyExistsError as err:
        raise TextXSemanticError(f"Instance with stack name '{definition.semantic_data.name}' already exists.", **get_location(definition)) from err

    print("Instance(s) processed\n")





 