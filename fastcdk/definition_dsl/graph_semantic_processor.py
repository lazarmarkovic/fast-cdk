from textx import get_location
from textx.exceptions import TextXSemanticError

from fastcdk.data_structure.errors import NodeAlreadyExistsError
from fastcdk.data_structure.graph import DirectedAcyclicGraph, GraphNode, NodeNotFoundError, NodeType
from fastcdk.definition_dsl.class_model import deep_copy_def
from fastcdk.junk.graph_viz import InteractiveDAG


class GraphSemanticProcessor:
  def __init__(self, definitions, stack_instance, other_instances):
    self.graph = DirectedAcyclicGraph()
    self.definitions = definitions

    self.stack_instance = stack_instance
    self.other_instances = other_instances

    print("Definitions passed: " + str(len(definitions)))
    print("Instances passed: " + str(len(other_instances.table) + 1))
    print("\n\n")


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


  def add_definitions(self):
    # Add definitions as pure nodes first
    print("Add Definitions")
    for definition in self.definitions:
      print("Definition name: " + definition.semantic_data.name)

      try:
        new_node = GraphNode(definition.semantic_data, NodeType.DEFINITION, definition.base_path)
        self.graph.add_node(new_node)
      except NodeAlreadyExistsError as err:
        raise TextXSemanticError(f"Definition with name '{definition.semantic_data.name}' already exists.", **get_location(definition)) from err

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

            new_node = GraphNode(def_deep_copy, NodeType.DEFINITION, node_to_copy.base_path, assigned_name=dep.assigned_name, edges=node_to_copy.edges)
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
    
    print("All Definition(s) processed\n")


  def add_instances(self):
    print("\n\n")
    print("Adding Instance with stack name: " + self.stack_instance.stack_name)

    # Add all instances connected to
    for oi_key in self.stack_instance.children:
      print("--- adding other instance: " + oi_key)
      if oi_key not in self.other_instances.table:
        raise TextXSemanticError(f"Instance with name '{oi_key}' is not defined.")
      oi_obj = self.other_instances.table[oi_key]

      # Find required definition to be used
      node_to_copy = self.graph.get_node(oi_obj.def_name)
      if node_to_copy is None:
        raise TextXSemanticError(f"Definition '{oi_obj.def_name}' for instance named '{oi_key}' not found.")
      
      # Make deep copy of definition
      def_deep_copy = deep_copy_def(node_to_copy.definition)
      oi_obj.apply_to(def_deep_copy)

      # Make new node with deep copy
      print("Creating instance of: " + oi_obj.def_name + " with new assigned name: " + oi_obj.assigned_name)
      new_node = GraphNode(def_deep_copy, NodeType.INSTANCE, node_to_copy.base_path, assigned_name=oi_obj.assigned_name, edges=node_to_copy.edges)
      self.graph.add_node(new_node)

    

  
    ############
    # Handle dep overrides separately
    # Find all dep override indicators
    print("\n\nHandling dep overrides")
    for oi_key in self.other_instances.table:
      oi_obj = self.other_instances.table[oi_key]
      oi_node = self.graph.get_node(oi_key)
      print("Processing dep overrides for instance: " + oi_key)
      for dov_oi_key in oi_obj.dep_overrides:
        print(" - dep override: " + dov_oi_key)
    
        # Create if it is not already created
        dov_node = self.graph.get_node(dov_oi_key)
        if dov_node is None:
          print(" - Creating dep override instance node: " + dov_oi_key)
          if dov_oi_key not in self.other_instances.table:
            raise TextXSemanticError(f"Instance for dependancy override '{dov_oi_key}' not found.")
          
          # Find required definition to be used
          dov_oi_obj = self.other_instances.table[dov_oi_key]
          node_to_copy = self.graph.get_node(dov_oi_obj.def_name)
          if node_to_copy is None:
            raise TextXSemanticError(f"Definition '{dov_oi_obj.def_name}' for instance named '{dov_oi_obj.assigned_name}' not found.")
          
          # Make deep copy of definition
          def_deep_copy = deep_copy_def(node_to_copy.definition)
          dov_oi_obj.apply_to(def_deep_copy)

          # Make new node with deep copy
          print(" - Creating instance of: " + dov_oi_obj.def_name + " with new assigned name: " + dov_oi_obj.assigned_name)
          new_node = GraphNode(def_deep_copy, NodeType.INSTANCE, node_to_copy.base_path, assigned_name=dov_oi_obj.assigned_name, edges=node_to_copy.edges)
          self.graph.add_node(new_node)
          dov_node = new_node
        else:
          print(" - Dep override node already exists: " + dov_oi_key)

        # Find the nodes which need to be replaced
        # only if the node is present
        if hasattr(oi_node, "edges"):
          for edge in oi_node.edges:
            edge_node = self.graph.get_node(edge)
            if edge_node.definition.name == dov_node.definition.name:
              print(f" -> Replacing parent edge from {oi_node.assigned_name} to {edge_node.assigned_name}")
              self.graph.replace_edge(oi_node.assigned_name, edge_node.assigned_name, dov_node.assigned_name)
          print("--------\n")
              




    ############
    # Add stack instance
    stack_node = self.graph.get_node("stack")
    stack_def_deep_copy = deep_copy_def(stack_node.definition)
    self.stack_instance.apply_to_stack_def(stack_def_deep_copy)
    new_stack_node = GraphNode(stack_def_deep_copy, NodeType.INSTANCE, stack_node.base_path, assigned_name=self.stack_instance.stack_name, edges=[])
    self.graph.add_node(new_stack_node)

    # Add stack instance children as edges in graph
    for child in self.stack_instance.children:
      to_node = self.graph.get_node(child)
      if to_node is None:
        raise TextXSemanticError(f"Instance or definition with name '{child}' is not found.")
      self.graph.add_edge(new_stack_node, to_node)
      


    print("All Instance(s) processed\n")


    #### >>>> TODO: Generate files and DONE!