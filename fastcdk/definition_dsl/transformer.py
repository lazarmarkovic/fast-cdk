
from dataclasses import asdict, dataclass
from functools import reduce
from types import SimpleNamespace
import json

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template

from fastcdk.data_structure.graph import DirectedAcyclicGraph

from fastcdk.util.print import to_plain


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
    

    def make_contexts_in_node(self, node):
      edge_node_contexts = [self.graph.get_node(e).contexts_as_edge for e in node.edges]
      merged_contexts_dict = reduce(lambda x, y: {**x, **y}, edge_node_contexts, {})

      plain = to_plain(node.definition.templates.table)
      print(json.dumps(plain, indent=2))
      this_template = node.definition.templates.table["this"]
     

      env_vars = {}
      for ev_key, ev_val in node.definition.env_vars.table.items():
        env_vars[ev_key] = ev_val.path_joined
      context_as_obj = SimpleNamespace(**{
        **asdict(this_template),
        **env_vars,
        **node.definition.default_inputs.table
      })
      #print(context_as_obj)
      

      contexts_as_edge = {
        node.original_assigned_name: context_as_obj
      }
      this_context = {
        "this": context_as_obj,
        **merged_contexts_dict,
        **{k: v for k, v in node.definition.templates.table.items() if k != "this"}
      }
      print("THIS CONTEXT: ")
      plain = to_plain(this_context)
      print(json.dumps(plain, indent=2))

      node.contexts_as_edge = contexts_as_edge
      node.this_context = this_context


    def make_renders_in_node(self, node):
      ## Must store the file path to get it here
      template_path = node.base_path
      jinja2_env = Environment(
        loader=FileSystemLoader(str(template_path)),
        trim_blocks=False,
        lstrip_blocks=False,
        undefined=StrictUndefined,  # raise if a var is missing
      )

      tn = list(node.definition.templates.table.keys())
      template_name = tn[0]
      template_file = node.definition.templates.table[template_name].template_file

      print("++++++ RENDERING: " + str(template_path)  + "/" + template_file)
      template = jinja2_env.get_template(template_file)
      node.rendered_class = template.render({**node.this_context, "render_class_def":True})
      node.rendered_constructor = template.render({**node.this_context, "render_class_def":False})


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

      real_nodes = [self.graph.get_node(n) for n in construct_init_order]
      for node in real_nodes:
        self.make_contexts_in_node(node)
        self.make_renders_in_node(node)
      print(real_nodes[3].rendered_class)

      # constructs = []
      # for node in construct_init_order:
      #   self.make_contexts_in_node(node)
      #   self.make_renders_in_node(node)

      # context = {
      #   "constructs": constructs,
      # }

      # template_path = stack_root_node.base_path
      # template_name = stack_root_node.definition.templates.table["stack"]
      # template_file = stack_root_node.definition.templates.table[template_name].template_file

      # print("render stack in: " + str(template_path)  + "/" + template_file)
      
      # jinja2_env = Environment(
      #   loader=FileSystemLoader(str(template_path)),
      #   trim_blocks=False,
      #   lstrip_blocks=False,
      #   undefined=StrictUndefined,  # raise if a var is missing
      # )
      
      # template = jinja2_env.get_template(template_file)
      # print(template.render(context))


    def generate_code(self, graph_node):
      pass