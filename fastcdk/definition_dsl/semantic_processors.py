
from textx import get_location
from textx.exceptions import TextXSemanticError

from fastcdk.definition_dsl.class_model import DefaultInputsSem, DefSem, DepSem, DepsSem, EnvVarSem, EnvVarsSem, InstancesSem, OtherInstanceSem, OtherInstancesSem, StackInstanceSem, TemplateMapSem, deep_copy_def


class SemanticProcessors:
  def __init__(self):
    self.definitions = []
    self.instances = []

    self.definitions = []
    self.obj_processors = {
      'TempalteMapSection': self.template_map_section, 
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
  

  def template_map_section(self, entity):
    generated_file_checks = set()
    table = {}
    for e in entity.entries:
      if e.template_file in table:
        raise TextXSemanticError( f"Duplicate template map key '{e.template_file}'.", **get_location(e))
      if e.generated_file in generated_file_checks:
        raise TextXSemanticError(f"Duplicate template map key '{e.generated_file}'.", **get_location(e))
      
      generated_file_checks.add(e.generated_file)
      table[e.template_file] = e.generated_file
    entity.semantic_data = TemplateMapSem(table=table)


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
      if i.key in {"path","id_prefix","name_prefix","class_prefix","class_name"} or i.key in extras:
        raise TextXSemanticError(f"Duplicate input variable '{i.key}' in default_inputs.", **get_location(i.key))
      extras[i.key] = i.val

    entity.semantic_data = DefaultInputsSem(
      path=entity.path.val,  
      id_prefix=entity.id_prefix.val,
      name_prefix=entity.name_prefix.val,
      class_prefix=entity.class_prefix.val,
      class_name=entity.class_name.val,
      extras=extras,
    )


  def dep_entry(self, entity):
    if (entity.assigned_name == entity.def_name):
      raise TextXSemanticError(f"Dep entry assigned_name '{entity.assigned_name}' cannot be the same as definition name.", **get_location(entity))

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
    templates = getattr(entity.template_map, "semantic_data", None) or TemplateMapSem({})
    deps = getattr(entity.deps, "semantic_data", None) or DepsSem({})
    envs = getattr(entity.env_vars, "semantic_data", None) or EnvVarsSem({})
    default_inputs = getattr(entity.default_inputs, "semantic_data", None) or DefaultInputsSem({})

    entity.semantic_data = DefSem(
      name=entity.name,
      templates=templates,
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
    # Validate children
    child_names = set()
    for c in entity.children:
      if c.name in child_names:
        raise TextXSemanticError(f"Duplicate child instance name '{c.name}' in stack_instance section.", **get_location(c))
      child_names.add(c.name)

    entity.semantic_data = StackInstanceSem(
      stack_name=entity.stack_name,
      aws_account_id=entity.aws_account_id.val,
      aws_region=entity.aws_region.val,
      aws_stack_name=entity.aws_stack_name.val,
      project=entity.project.val,
      exe_env=entity.exe_env.val,
      children=tuple(child_names)
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
    new_definitions = getattr(model.fcdk, "definitions", None) or []
    new_instances = getattr(model.fcdk, "instances", None) or []

    self.definitions.extend(new_definitions)
    self.instances.extend(new_instances)

