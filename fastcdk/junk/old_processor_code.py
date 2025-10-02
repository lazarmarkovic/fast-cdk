

  def env_var(self, entity):
    entity.semantic_data = {
      'name': entity.key, 
      'path_joined': ".".join(entity.ref.parts), 
      'path_parts': entity.ref.parts, 
      'value': entity.val
    }
  

  def env_vars_section(self, entity):
    entity.semantic_data = {env_var.semantic_data['name']: env_var.semantic_data for env_var in entity.entries}
  
  


def default_inputs_section(self, entity):
    data = {
      'id_prefix': entity.id_prefix.val,
      'name_prefix': entity.name_prefix.val,
      'class_prefix': entity.class_prefix.val,
      'class_name': entity.class_name.val,
    }
    for i in entity.inputs:
      if (i.key in data):
        raise TextXSemanticError(f"Duplicate input variable '{i.key}' in default_inputs section.", **get_location(i))
      data[i.key] = i.val
    entity.semantic_data = data


  def dep_entry(self, entity):
    if (entity.assigned_name == entity.def_name):
      raise TextXSemanticError(f"Dep entry assigned_name '{entity.assigned_name}' cannot be the same as definition name.", **get_location(entity))
    if (entity.assigned_name == entity.source_assigned_name or entity.def_name == entity.source_assigned_name):
      raise TextXSemanticError(f"Dep entry source_assigned_name '{entity.source_assigned_name}' cannot be the same as assigned name or definition name.", **get_location(entity)) 
    data = {
      'assigned_name': entity.assigned_name,
      'def_name': entity.def_name,
      'source_assigned_name': entity.source_assigned_name,
      'props': {}
    }
    for i in entity.props:
      if (i.key in data['props']):
        raise TextXSemanticError(f"Duplicate input variable '{i.key}' in dep_entry section.", **get_location(i))
      data['props'][i.key] = i.val
    entity.semantic_data = data


  def deps_section(self, entity):
    data = {}
    for dep in entity.entries:
      if (dep.semantic_data['assigned_name'] in data):
        raise TextXSemanticError(f"Duplicate dep assigned name '{dep.semantic_data['assigned_name']}' in deps section.", **get_location(dep))
      data[dep.semantic_data['assigned_name']] = dep.semantic_data
    entity.semantic_data = data
  

  def definition(self, entity):
    data = {
      'name': entity.name,
      'template_file': entity.template_file.val,
      'default_path': entity.default_path.val,
      
      'deps': entity.deps.semantic_data,
      'env_vars': entity.env_vars.semantic_data,

      'default_inputs': entity.default_inputs.semantic_data,
    }
    entity.semantic_data = data
    self.definitions.append(data)

    print(f"Definition processed: {entity.name}")