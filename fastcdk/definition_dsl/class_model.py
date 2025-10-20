from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Union

Value = Union[str, int, float, bool, None]



##########################
###### Definition class model
@dataclass
class SingleDefinition:
  name: str
  templates: TemplateMap
  deps: DependencyMap
  env_vars: EnvVarMap
  default_inputs: DefaultInputMap


@dataclass
class SingleTemplate:
  import_path: str
  template_name: str
  template_file: str
  gen_path: str
  gen_file_name: str
  var_name: str
  class_name: str
  id_prefix: str
  name_prefix: str


@dataclass
class TemplateMap:
  table: Mapping[str, SingleTemplate] = field(default_factory=dict)


@dataclass
class SingleEnvVar:
  name: str
  path_joined: str
  path_parts: tuple[str, ...]
  value: Value = None


@dataclass
class EnvVarMap:
  table: Mapping[str, SingleEnvVar] = field(default_factory=dict)


@dataclass
class DefaultInputMap:
  table: Mapping[str, Value] = field(default_factory=dict)


class SingleGeneralInputType(Enum):
  REGULAR_INPUT = 0
  TEMPLATE_INPUT = 1
  ENV_VAR_INPUT = 2


@dataclass
class SingleGeneralInput:
  type: SingleGeneralInputType
  key: str | tuple
  val: Value | SingleEnvVar

class ApplicableToDef:
  def apply_to(self, definition: SingleDefinition):
    for _, input_obj in self.inputs.items():
      print("INPUTTT: " + str(input_obj.key))
      if input_obj.type == SingleGeneralInputType.REGULAR_INPUT:
        definition.default_inputs.table[input_obj.key] = input_obj.val
      elif input_obj.type == SingleGeneralInputType.ENV_VAR_INPUT:
        definition.env_vars.table[input_obj.key].path_joined = input_obj.val.path_joined
        definition.env_vars.table[input_obj.key].path_parts = input_obj.val.path_parts
        if input_obj.val.value is not None:
          definition.env_vars.table[input_obj.key].value = input_obj.val.value
      elif input_obj.type == SingleGeneralInputType.TEMPLATE_INPUT:
        #setattr(obj, atrr_name, attr_value)
        setattr(definition.templates.table[input_obj.key[0]], input_obj.key[1], input_obj.val)
      else:
        raise Exception("Not found.")
  

@dataclass
class SingleDependency(ApplicableToDef):
  original_assigned_name: str
  assigned_name: str
  def_name: str
  inputs: Mapping[str | tuple, SingleGeneralInput] = field(default_factory=dict)
  
  

@dataclass
class DependencyMap:
  table: Mapping[str, SingleDependency] = field(default_factory=dict)



##########################
###### Instance class model

@dataclass
class SingleOtherInstance(ApplicableToDef):
  assigned_name: str
  def_name: str
  inputs: Mapping[str | tuple, SingleGeneralInput] = field(default_factory=dict)
  dep_overrides: tuple[str, ...] = field(default_factory=tuple)
  

@dataclass
class OtherInstanceMap:
  table: Mapping[str, SingleOtherInstance] = field(default_factory=dict)


@dataclass
class SingleStackInstance(ApplicableToDef):
  stack_name: str
  inputs: Mapping[str | tuple, SingleGeneralInput] = field(default_factory=dict)
  children: tuple[str, ...] = field(default_factory=tuple)

  def apply_to_stack_def(self, stack_def):
    super().apply_to(stack_def)


    # add children as deps
    for child in self.children:
      if child not in stack_def.deps.table:
        stack_def.deps.table[child] = SingleDependency(
          original_assigned_name=child,
          assigned_name=child,
          def_name=child,
          inputs={},
        )


@dataclass
class SingleInstance:
  stack_instance: SingleStackInstance
  other_instances: SingleOtherInstance


####################
## DEEP COPY

def deep_copy_def(src: SingleDefinition) -> SingleDefinition:
  # --- helpers ---
  def copy_template(t: SingleTemplate) -> SingleTemplate:
    return SingleTemplate(
      import_path=t.import_path,
      template_name=t.template_name,
      template_file=t.template_file,
      gen_path=t.gen_path,
      gen_file_name=t.gen_file_name,
      var_name=t.var_name,
      class_name=t.class_name,
      id_prefix=t.id_prefix,
      name_prefix=t.name_prefix,
    )

  def copy_envvar(ev: SingleEnvVar) -> SingleEnvVar:
    return SingleEnvVar(
      name=ev.name,
      path_joined=ev.path_joined,
      path_parts=tuple(ev.path_parts),
      value=ev.value,
    )

  def copy_inputs(inp_map: Mapping[str | tuple, Value | SingleEnvVar]) -> Dict[str | tuple, Value | SingleEnvVar]:
    out: Dict[str | tuple, Value | SingleEnvVar] = {}
    for k, v in inp_map.items():
      if isinstance(v, SingleEnvVar):
        out[k] = copy_envvar(v)
      else:
        # Value is primitive (str/int/float/bool/None) – safe to reuse
        out[k] = v
    return out

  def copy_dependency(d: SingleDependency) -> SingleDependency:
    return SingleDependency(
      original_assigned_name=d.original_assigned_name,
      assigned_name=d.assigned_name,
      def_name=d.def_name,
      inputs=copy_inputs(d.inputs),
    )

  # --- copy leaf maps ---
  new_templates_table: Dict[str, SingleTemplate] = {
    k: copy_template(v) for k, v in src.templates.table.items()
  }
  new_envvars_table: Dict[str, SingleEnvVar] = {
    k: copy_envvar(v) for k, v in src.env_vars.table.items()
  }
  new_default_inputs_table: Dict[str, Value] = dict(src.default_inputs.table)
  new_deps_table: Dict[str, SingleDependency] = {
    k: copy_dependency(v) for k, v in src.deps.table.items()
  }

  # --- reassemble ---
  return SingleDefinition(
    name=src.name,
    templates=TemplateMap(table=new_templates_table),
    deps=DependencyMap(table=new_deps_table),
    env_vars=EnvVarMap(table=new_envvars_table),
    default_inputs=DefaultInputMap(table=new_default_inputs_table),
  )
