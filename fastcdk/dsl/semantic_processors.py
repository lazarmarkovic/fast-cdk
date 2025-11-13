
from textx import get_location  # noqa: I001
from textx.exceptions import TextXSemanticError


from fastcdk.dsl.class_model import (
  SingleDefinition, 

  TemplateMap,
  SingleTemplate,

  DefaultInputMap,

  SingleGeneralInputType,
  SingleGeneralInput,

  SingleDependency, 
  DependencyMap, 

  SingleEnvVar, 
  EnvVarMap,

  SingleInstance, 

  SingleOtherInstance, 
  OtherInstanceMap,

  SingleStackInstance,
)


class SemanticProcessors:
  def __init__(self):
    self.definitions = []
    self.instances = [] 
 
    self.obj_processors = {
      'SingleTemplate': self.single_template,
      'TemplateMapSection': self.template_map_section,

      'SingleGeneralInputAssign': self.single_general_input_assign,
      'SingleDependency': self.single_dependency,
      'DependencyMapSection': self.dependency_map_section,

      'SingleEnvVar': self.single_env_var,
      'EnvVarMapSection': self.env_var_map_section,

      'SingleDefaultInputAssign': self.single_general_input_assign,
      'DefaultInputMapSection': self.default_input_map_section,

      'SingleDefinition': self.definition,

      
      'SingleOtherInstance': self.single_other_instance,
      'SingleStackInstance': self.single_stack_instance,

      'Instances': self.instances_section,
    }

    self.template_field_map = {
      "TemplateFileAssign": "template_file",
      "GenPathAssign": "gen_path",
      "GenFileNameAssign": "gen_file_name",
      "VarNameAssign": "var_name",
      "ClassNameAssign": "class_name",
      "IdPrefixAssign": "id_prefix",
      "NamePrefixAssign": "name_prefix",
    }


  #########################
  ##### Definition processors
  def _join_ref_parts(self, ref) -> list[str]:
    return [ref.first, *list(ref.rest)]
  

  def single_template(self, entity):
    entity.semantic_data = SingleTemplate(
      import_path = "",
      template_name=entity.template_name,
      template_file=entity.template_file.val,
      gen_path=entity.gen_path.val,
      gen_file_name=entity.gen_file_name.val,
      var_name=entity.var_name.val,
      class_name=entity.class_name.val,
      id_prefix=entity.id_prefix.val,
      name_prefix=entity.name_prefix.val,
    )
  

  def template_map_section(self, entity):
    table = {}
    for e in entity.entries:
      sem_data = e.semantic_data
      if sem_data.template_name in table:
        raise TextXSemanticError( f"Duplicate template name '{sem_data.template_name}'.", **get_location(e))
      table[sem_data.template_name] = sem_data
    entity.semantic_data = TemplateMap(table=table)


  def single_general_input_assign(self, entity):
    if getattr(entity, "ref", None) is not None:
      parts = self._join_ref_parts(entity.ref)
      entity.semantic_data = SingleGeneralInput(
        type=SingleGeneralInputType.ENV_VAR_INPUT,
        key=entity.key,
        val=SingleEnvVar(
          name=entity.key,
          path_joined=".".join(parts),
          path_parts=tuple(parts),
          value=getattr(entity, "val", None),
        )
      )
    elif getattr(entity, "ref_val", None) is not None:
      entity.semantic_data = SingleGeneralInput(
        type=SingleGeneralInputType.ENV_VAR_INPUT,
        key=entity.key,
        val=SingleEnvVar(
          name=entity.key,
          path_joined="",
          path_parts=(),
          value=getattr(entity, "ref_val", None),
        )
      )
    elif getattr(entity, "val", None) is not None:
      entity.semantic_data = SingleGeneralInput(
        type=SingleGeneralInputType.REGULAR_INPUT,
        key=entity.key,
        val=entity.val
      )
    elif getattr(entity, "template_name", None) is not None and getattr(entity, "template_field", None) is not None:
      field_name = self.template_field_map.get(entity.template_field.__class__.__name__)
      entity.semantic_data = SingleGeneralInput(
        type=SingleGeneralInputType.TEMPLATE_INPUT,
        key=(entity.template_name, field_name),
        val=entity.template_field.val
      )
    else:
      raise TextXSemanticError("Invalid dependancy input.", **get_location(entity))


  def single_dependency(self, entity):
    if (entity.assigned_name == entity.def_name):
      raise TextXSemanticError(f"Dep entry assigned_name '{entity.assigned_name}' cannot be the same as definition name.", **get_location(entity))
    inputs_dict = {}
    for i in entity.inputs:
      single_input = i.semantic_data
      if (single_input.key in inputs_dict):
        raise TextXSemanticError(f"Duplicate input variable '{".".join(single_input.key)}' in dep_entry section.", **get_location(i))
      inputs_dict[single_input.key] = single_input
    entity.semantic_data = SingleDependency(
      assigned_name=entity.assigned_name,
      def_name=entity.def_name if entity.def_name != '' else entity.assigned_name,
      inputs=inputs_dict
    )


  def dependency_map_section(self, entity):
    table = {}
    for dep in entity.entries:
      k = dep.semantic_data.assigned_name
      if k in table:
        raise TextXSemanticError(f"Duplicate dep assigned name '{k}' in deps section.", **get_location(dep))
      table[k] = dep.semantic_data
    entity.semantic_data = DependencyMap(table=table)


  def single_env_var(self, entity):
    parts = self._join_ref_parts(entity.ref)
    entity.semantic_data = SingleEnvVar(
      name=entity.key,
      path_joined=".".join(parts),
      path_parts=tuple(parts),
      value=entity.val
    )


  def env_var_map_section(self, entity):
    entity.semantic_data = EnvVarMap(
      table={ev.semantic_data.name: ev.semantic_data for ev in entity.entries}
    )


  def default_input_map_section(self, entity):
    table = {}
    for i in entity.inputs:
      single_input = i
      if (single_input.key in table):
        raise TextXSemanticError(f"Duplicate input variable '{single_input.key}' in dep_entry section.", **get_location(i))
      table[single_input.key] = single_input
    entity.semantic_data = DefaultInputMap(table=table)


  def definition(self, entity):
    templates = getattr(entity.template_map, "semantic_data", None) or TemplateMap({})
    deps = getattr(entity.deps, "semantic_data", None) or DependencyMap({})
    envs = getattr(entity.env_vars, "semantic_data", None) or EnvVarMap({})
    default_inputs = getattr(entity.default_inputs, "semantic_data", None) or DefaultInputMap({})

    entity.semantic_data = SingleDefinition(
      name=entity.name,
      templates=templates,
      deps=deps,
      env_vars=envs,
      default_inputs=default_inputs,
    )
  

  #########################
  ##### Instance processors
  def single_other_instance(self, entity):
    if entity.assigned_name == entity.target_name:
      raise TextXSemanticError(
        f"Dep entry assigned_name '{entity.assigned_name}' cannot be the same as definition name.",
        **get_location(entity),
      )

    inputs_dict: dict = {}
    dep_overrides: list[str] = []

    for item in entity.body:
      cls_name = item.__class__.__name__

      if cls_name == "SingleGeneralInputAssign":
        single_input = item.semantic_data
        key = single_input.key
        if key in inputs_dict:
          # if key is a tuple like ('tmpl', 'field') we join with '.'
          key_str = ".".join(key) if isinstance(key, tuple) else str(key)
          raise TextXSemanticError(
            f"Duplicate input variable '{key_str}' in instance section.",
            **get_location(item),
          )
        inputs_dict[key] = single_input

      elif cls_name == "DepOverride":
        dep_overrides.append(item.name)

      else:
        raise TextXSemanticError(
          f"Unknown element '{cls_name}' inside other-instance body.",
          **get_location(item),
        )

    entity.semantic_data = SingleOtherInstance(
      assigned_name=entity.assigned_name,
      target_name=entity.target_name or entity.assigned_name,
      inputs=inputs_dict,
      dep_overrides=tuple(dep_overrides),
    )



  def single_stack_instance(self, entity):
    child_names: set[str] = set()
    inputs_dict: dict = {}

    for item in entity.body:
      cls_name = item.__class__.__name__

      if cls_name == "SingleGeneralInputAssign":
        single_input = item.semantic_data
        key = single_input.key
        if key in inputs_dict:
          key_str = ".".join(key) if isinstance(key, tuple) else str(key)
          raise TextXSemanticError(
            f"Duplicate input variable '{key_str}' in stack_instance section.",
            **get_location(item),
          )
        inputs_dict[key] = single_input

      elif cls_name == "Child":
        if item.name in child_names:
          raise TextXSemanticError(
            f"Duplicate child instance name '{item.name}' in stack_instance section.",
            **get_location(item),
          )
        child_names.add(item.name)

      else:
        raise TextXSemanticError(
          f"Unknown element '{cls_name}' inside stack body.",
          **get_location(item),
        )

    entity.semantic_data = SingleStackInstance(
      stack_name=entity.stack_name,
      inputs=inputs_dict,
      children=tuple(child_names),
    )




  def instances_section(self, entity):
    print("ENTER")
    stack_sem: SingleStackInstance | None = None
    other_instances_table: dict[str, SingleOtherInstance] = {}

    for inst in entity.instances:
      sem = inst.semantic_data

      if isinstance(sem, SingleStackInstance):

        print("FOOOOUND. " + sem.stack_name)
        if stack_sem is not None:
          raise TextXSemanticError(
            "Only one stack instance is allowed per file.",
            **get_location(inst),
          )
        stack_sem = sem

      elif isinstance(sem, SingleOtherInstance):
        k = sem.assigned_name
        if k in other_instances_table:
          raise TextXSemanticError(
            f"Duplicate instance name '{k}' in instance section.",
            **get_location(inst),
          )
        other_instances_table[k] = sem

      else:
        raise TextXSemanticError(
          f"Unexpected semantic type '{type(sem).__name__}' in Instances.",
          **get_location(inst),
        )

    if stack_sem is None:
      raise TextXSemanticError(
        "Exactly one stack instance is required in the file, but none was found.",
        **get_location(entity),
      )
    
    print("stack name: " + stack_sem.stack_name)

    entity.semantic_data = SingleInstance(
      stack_instance=stack_sem,
      other_instances=OtherInstanceMap(table=other_instances_table),
    )




  # ###### MODEL PROCESSING ######
  # def model_processor(self, model, metamodel):
  #   new_definitions = getattr(model.fcdk, "definitions", None) or []
  #   new_instances = getattr(model.fcdk, "instances", None) or []

  #   self.definitions.extend(new_definitions)
  #   self.instances.extend(new_instances)

