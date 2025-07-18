class DefaultInputsSection:
  def __init__(self, id_prefix, name_prefix, class_prefix, class_name):
    self.id_prefix = id_prefix
    self.name_prefix = name_prefix
    self.class_prefix = class_prefix
    self.class_name = class_name

  def add_input(self, input_name, input_value):
    setattr(self, input_name, input_value)


class FcdkDef:
  def __init__(self, name, template_file, default_path, deps_section=None, env_vars_section=None, default_inputs_section=None):
    self.name = name
    self.template_file = template_file
    self.default_path = default_path
    self.deps_section = deps_section
    self.env_vars_section = env_vars_section
    self.default_inputs_section = default_inputs_section
