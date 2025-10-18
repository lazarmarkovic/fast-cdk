
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template

from fastcdk.data_structure.graph import DirectedAcyclicGraph


class InputObject:
  def __init__(self):
    pass

  def add_input(self, input_name, input_value):
    setattr(self, input_name, input_value)

  def get_dict(self):
    d = dict()
    for name, value in vars(self).items():
      if not name.startswith("_"):
        d[name] = "" if value == "null" else value
    return d

  def is_empty(self):
    return not any(value for value in vars(self).values() if not value.startswith("_"))


class Transformer:
    def __init__(self, graph: DirectedAcyclicGraph):
        self.graph = graph
        self.file_list = []

    def get_root_node(self):
      for node_name in self.graph.get_nodes():
        if self.graph.get_node(node_name).definition.name == "stack" and node_name != "stack":
          return self.graph.get_node(node_name)

    def lowercase_first(self, s):
      return s[0].lower() + s[1:] if s else s

    def to_files_list(self):
      stack_root_node = self.get_root_node()
      nodes_in_use = self.graph.usage_layers(stack_root_node.assigned_name)
      
      construct_init_order = []
      print("\n\nTest transformer to_files_list")
      for layer in nodes_in_use:
        print("\nLayer:")
        for i in layer:
          construct_init_order.append(i)
          print("Node in use: " + i)
      construct_init_order.remove(stack_root_node.assigned_name)

      constructs = []
      for n in construct_init_order:
        node = self.graph.get_node(n)
        tn = list(node.definition.templates.table.keys())
        template_name = tn[0]
        gen_file_name = node.definition.templates.table[template_name].gen_file_name
        gen_path = node.definition.templates.table[template_name].gen_path
        class_name = node.definition.templates.table[template_name].class_name
        path =  gen_path + "/" + gen_file_name if gen_path != "/" else "/" + gen_file_name
        constructs.append({
          "class": class_name,
          "path": path,
          "instance_name": self.lowercase_first(class_name),
        })

      context = {
        "constructs": constructs,
      }


      ## Must store the file path to get it here
      template_path = stack_root_node.base_path
      jinja2_env = Environment(
        loader=FileSystemLoader(str(template_path)),
        trim_blocks=False,
        lstrip_blocks=False,
        undefined=StrictUndefined,  # raise if a var is missing
      )

      tn = list(stack_root_node.definition.templates.table.keys())
      template_name = tn[0]

      print("template name: " + template_name)
      template_file = stack_root_node.definition.templates.table[template_name].template_file

      print("++++++ " + str(template_path)  + "/" + template_file)

      template = jinja2_env.get_template(template_file)
      print("template: " + template_file)
      print(template.render(context))


    def generate_code(self, graph_node):
      pass