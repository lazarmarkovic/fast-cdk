from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, Mapping, Tuple, Union

Value = Union[str, int, float, bool, None]


##########################
###### Definition class model
@dataclass
class TemplateMapSem:
  # map "template.j2" -> "generated.ts" (both as dotted strings from RefPath)
  table: Mapping[str, str] = field(default_factory=dict)

  def to_dict(self) -> Dict[str, str]:
    return dict(self.table)
  

@dataclass
class EnvVarSem:
  name: str
  path_joined: str
  path_parts: Tuple[str, ...]
  value: Value

  def to_dict(self) -> Dict[str, Any]:
    return {
      "name": self.name,
      "path_joined": self.path_joined,
      "path_parts": list(self.path_parts),
      "value": self.value,
    }


@dataclass
class EnvVarsSem:
  table: Mapping[str, EnvVarSem] = field(default_factory=dict)

  def to_dict(self) -> Dict[str, Any]:
    return {k: v.to_dict() for k, v in self.table.items()}


@dataclass
class DefaultInputsSem:
  path: str
  id_prefix: str
  name_prefix: str
  class_prefix: str
  class_name: str
  extras: Mapping[str, Value] = field(default_factory=dict)

  def to_dict(self) -> Dict[str, Value]:
    base: Dict[str, Value] = {
      "path": self.path,
      "id_prefix": self.id_prefix,
      "name_prefix": self.name_prefix,
      "class_prefix": self.class_prefix,
      "class_name": self.class_name,
    }
    base.update(dict(self.extras))
    return base


@dataclass
class DepSem:
  assigned_name: str
  def_name: str
  props: Mapping[str, Value | EnvVarsSem] = field(default_factory=dict)

  def to_dict(self) -> Dict[str, Any]:
    return {
      "assigned_name": self.assigned_name,
      "def_name": self.def_name,
      "props": dict(self.props),
    }
  
  def apply_to(self, definition: DefSem):
    for p in self.props:
      match p:
        case "path":
          definition.default_inputs.path = self.props[p]
        case "id_prefix":
          definition.default_inputs.id_prefix = self.props[p]
        case "name_prefix":
          definition.default_inputs.name_prefix = self.props[p]
        case "class_prefix":
          definition.default_inputs.class_prefix = self.props[p]
        case "class_name":
          definition.default_inputs.class_name = self.props[p]
        case _:
          if p in definition.env_vars.table and isinstance(self.props[p], EnvVarsSem):
              definition.env_vars.table[p].path_joined = self.props[p].path_joined
              definition.env_vars.table[p].path_parts = self.props[p].path_parts
          elif p in definition.default_inputs.extras:
            definition.default_inputs.extras[p] = self.props[p]
          else:
            raise Exception("Not found.")



@dataclass
class DepsSem:
  table: Mapping[str, DepSem] = field(default_factory=dict)

  def to_dict(self) -> Dict[str, Any]:
    return {k: v.to_dict() for k, v in self.table.items()}


@dataclass
class DefSem:
  name: str
  templates: TemplateMapSem  
  deps: DepsSem
  env_vars: EnvVarsSem
  default_inputs: DefaultInputsSem

  def to_dict(self) -> Dict[str, Any]:
    return {
      "name": self.name,
      "templates": self.templates.to_dict(),
      "deps": self.deps.to_dict(),
      "env_vars": self.env_vars.to_dict(),
      "default_inputs": self.default_inputs.to_dict(),
    }



##########################
###### Instance class model

@dataclass
class OtherInstanceSem:
  assigned_name: str
  def_name: str
  inputs: Mapping[str, Value | EnvVarSem] = field(default_factory=dict)
  dep_overrides: Tuple[str, ...] = field(default_factory=tuple)

  def to_dict(self) -> Dict[str, Any]:
    return {
      "assigned_name": self.assigned_name,
      "def_name": self.def_name,
      "inputs": {
        k: (v.to_dict() if isinstance(v, EnvVarSem) else v)
        for k, v in self.inputs.items()
      },
      "dep_overrides": list(self.dep_overrides),
    }
  
  def apply_to(self, definition: DefSem):
    for p in self.inputs:
      match p:
        case "path":
          definition.default_inputs.path = self.inputs[p]
        case "id_prefix":
          definition.default_inputs.id_prefix = self.inputs[p]
        case "name_prefix":
          definition.default_inputs.name_prefix = self.inputs[p]
        case "class_prefix":
          definition.default_inputs.class_prefix = self.inputs[p]
        case "class_name":
          definition.default_inputs.class_name = self.inputs[p]
        case _:
          if p in definition.env_vars.table and isinstance(self.inputs[p], EnvVarSem):
              definition.env_vars.table[p].path_joined = self.inputs[p].path_joined
              definition.env_vars.table[p].path_parts = self.inputs[p].path_parts
          elif p in definition.default_inputs.extras:
            definition.default_inputs.extras[p] = self.inputs[p]
          else:
            raise Exception(f"Input {p} is not found in definition {definition.name} input list.")
  

@dataclass
class OtherInstancesSem:
  table: Mapping[str, OtherInstanceSem] = field(default_factory=dict)

  def to_dict(self) -> Dict[str, Any]:
    return {k: v.to_dict() for k, v in self.table.items()}


@dataclass
class StackInstanceSem:
  stack_name: str
  aws_account_id: str
  aws_region: str
  aws_stack_name: Value
  project: Value
  exe_env: Value
  inputs: Mapping[str, Value | EnvVarSem] = field(default_factory=dict)
  children: Tuple[str, ...] = field(default_factory=tuple)

  def to_dict(self) -> Dict[str, Any]:
    return {
      "stack_name": self.stack_name,
      "aws_account_id": self.aws_account_id,
      "aws_region": self.aws_region,
      "aws_stack_name": self.aws_stack_name,
      "project": self.project,
      "exe_env": self.exe_env,
      "inputs": {
        k: (v.to_dict() if isinstance(v, EnvVarSem) else v)
        for k, v in self.inputs.items()
      },
      "children": list(self.children),
    }
  
  def apply_to_stack_def(self, stack_def):
    for p in self.inputs:
      match p:
        case "path":
          stack_def.default_inputs.path = self.inputs[p]
        case "id_prefix":
          stack_def.default_inputs.id_prefix = self.inputs[p]
        case "name_prefix":
          stack_def.default_inputs.name_prefix = self.inputs[p]
        case "class_prefix":
          stack_def.default_inputs.class_prefix = self.inputs[p]
        case "class_name":
          stack_def.default_inputs.class_name = self.inputs[p]
        case _:
          if p in stack_def.env_vars.table and isinstance(self.inputs[p], EnvVarsSem):
              stack_def.env_vars.table[p].path_joined = self.inputs[p].path_joined
              stack_def.env_vars.table[p].path_parts = self.inputs[p].path_parts
          elif p in stack_def.default_inputs.extras:
            stack_def.default_inputs.extras[p] = self.inputs[p]
          else:
            raise Exception("Not found.")
          
    stack_def.default_inputs.extras["stack_name"] = self.stack_name
    stack_def.default_inputs.extras["aws_account_id"] = self.aws_account_id
    stack_def.default_inputs.extras["aws_region"] = self.aws_region
    stack_def.default_inputs.extras["aws_stack_name"] = self.aws_stack_name
    stack_def.default_inputs.extras["project"] = self.project
    stack_def.default_inputs.extras["exe_env"] = self.exe_env

    # add children as deps
    for child in self.children:
      if child not in stack_def.deps.table:
        stack_def.deps.table[child] = DepSem(
          assigned_name=child,
          def_name=child,
          props={},
        )



@dataclass
class InstancesSem:
  stack_instance: StackInstanceSem
  other_instances: OtherInstancesSem

  def to_dict(self) -> Dict[str, Any]:
    return {
      "stack_instance": self.stack_instance.to_dict(),
      "other_instances": self.other_instances.to_dict(),
    }



################
########## UTILS
def sem_to_dict(obj: Any) -> Any:
  if hasattr(obj, "to_dict"):
    return obj.to_dict()  # our classes
  if is_dataclass(obj):
    return asdict(obj)    # fallback for other dataclasses
  if isinstance(obj, Mapping):
    return {k: sem_to_dict(v) for k, v in obj.items()}
  if isinstance(obj, (list, tuple)):
    return [sem_to_dict(v) for v in obj]
  return obj


#### Util for deep copy

def _deep_copy_envvar(ev: EnvVarSem) -> EnvVarSem:
  return EnvVarSem(
    name=ev.name,
    path_joined=ev.path_joined,
    path_parts=tuple(ev.path_parts),
    value=ev.value,
  )

def _deep_copy_envvars(evs: EnvVarsSem) -> EnvVarsSem:
  new_table: Dict[str, EnvVarSem] = {k: _deep_copy_envvar(v) for k, v in evs.table.items()}
  return EnvVarsSem(table=new_table)

def _deep_copy_default_inputs(di: DefaultInputsSem) -> DefaultInputsSem:
  return DefaultInputsSem(
    path=di.path,
    id_prefix=di.id_prefix,
    name_prefix=di.name_prefix,
    class_prefix=di.class_prefix,
    class_name=di.class_name,
    extras=dict(di.extras),
  )

def _deep_copy_dep(dep: DepSem) -> DepSem:
  def _clone_prop(v: Any) -> Any:
    # handle both single env-var and a table, plus primitives
    if isinstance(v, EnvVarSem):
        return _deep_copy_envvar(v)
    if isinstance(v, EnvVarsSem):
        return _deep_copy_envvars(v)
    # primitives: str/int/float/bool/None
    return v

  new_props: Dict[str, Any] = {k: _clone_prop(v) for k, v in dep.props.items()}
  return DepSem(
    assigned_name=dep.assigned_name,
    def_name=dep.def_name,
    props=new_props,
  )

def _deep_copy_deps(deps: DepsSem) -> DepsSem:
  new_table: Dict[str, DepSem] = {k: _deep_copy_dep(v) for k, v in deps.table.items()}
  return DepsSem(table=new_table)

def _deep_copy_templates(tm: TemplateMapSem) -> TemplateMapSem:
  return TemplateMapSem(table=dict(tm.table))

def deep_copy_def(defn: DefSem) -> DefSem:
  return DefSem(
    name=defn.name,
    templates=_deep_copy_templates(defn.templates),
    deps=_deep_copy_deps(defn.deps),
    env_vars=_deep_copy_envvars(defn.env_vars),
    default_inputs=_deep_copy_default_inputs(defn.default_inputs),
  )
