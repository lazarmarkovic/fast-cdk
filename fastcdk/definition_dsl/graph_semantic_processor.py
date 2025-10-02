from fastcdk.data_structure.graph import GraphNode, NodeNotFoundError, NodeType
from fastcdk.definition_dsl.class_model import deep_copy_def
from fastcdk.junk.graph_viz import InteractiveDAG


class GraphSemanticProcessor:
  def __init__(self, graph):
    self.graph = graph
    pass


  def visualize(self):
    nodes = self.graph.get_nodes()
    edges = self.graph.get_edges() 
    print("\n\n")
    print("EDGES:")
    for e in edges:
      print(e)

    # Create and visualize DAG
    dag = InteractiveDAG(nodes=nodes, edges=edges)
    dag.show()


  def make_global_dep_graph(self):
    # Make all nodes with custom assigned_name / "instances of defs"
    for node_name in self.graph.get_nodes():
      node = self.graph.get_node(node_name)
      if node.definition.deps is not None:
        for dep_key in node.definition.deps.table:
          dep = node.definition.deps.table[dep_key]
          if (dep.assigned_name != dep.def_name 
                and not self.graph.node_exists(dep.assigned_name) 
                and self.graph.node_exists(dep.def_name)
              ):
            print("Create copy of: " + dep.def_name + " with new name:" + dep.assigned_name)

            node_to_copy = self.graph.get_node(dep.def_name)
            def_deep_copy = deep_copy_def(node_to_copy.definition)
            dep.apply_to(def_deep_copy)

            new_node = GraphNode(def_deep_copy, NodeType.DEFINITION, assigned_name=dep.assigned_name, edges=node_to_copy.edges)
            self.graph.add_node(new_node)


    # Now add assigned nodes and edges
    for node_name in self.graph.get_nodes():
      node = self.graph.get_node(node_name)
      print("Finding edges from: " + node.assigned_name)
      if node.definition.deps is not None:
        for dep_key in node.definition.deps.table:
          dep = node.definition.deps.table[dep_key]
          print("dep: " + dep.def_name + "  " + dep.assigned_name)
          if dep.assigned_name == dep.def_name:
            to_node = self.graph.get_node(dep.def_name)
            if to_node is not None:
              self.graph.add_edge(node, to_node)
            else:
              raise NodeNotFoundError(dep.def_name)

          elif self.graph.node_exists(dep.assigned_name):
            to_node = self.graph.get_node(dep.assigned_name)
            self.graph.add_edge(node, to_node)
          
          else:
            pass
            # Not needed, it is handled above
            # new_node = GraphNode(fcdk_def, False, dep.assigned_name, dep.input)