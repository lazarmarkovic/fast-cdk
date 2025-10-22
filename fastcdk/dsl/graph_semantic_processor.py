from textx import get_location
from textx.exceptions import TextXSemanticError

from fastcdk.data_structure.chain import reverse_chains_allow_merges
from fastcdk.data_structure.errors import NodeAlreadyExistsError
from fastcdk.data_structure.graph import DirectedAcyclicGraph, GraphNode, NodeNotFoundError, NodeType
from fastcdk.dsl.class_model import deep_copy_def
from fastcdk.dsl.graph_viz import InteractiveDAG


class GraphSemanticProcessor:
  def __init__(self, definitions, stack_instance, other_instances):
    self.graph = DirectedAcyclicGraph()
    self.definitions = definitions

    self.stack_instance = stack_instance
    self.other_instances = other_instances

    print("Definitions passed: " + str(len(definitions)))
    print("Instances passed: " + str(len(other_instances.table) + 1))
    print("\n")


  def visualize(self):
    nodes = self.graph.get_nodes()
    edges = self.graph.get_edges() 
    # print("EDGES:")
    # for e in edges:
    #   print(e)

    # Create and visualize DAG
    dag = InteractiveDAG(nodes=nodes, edges=edges)
    dag.show()


  def add_definitions(self):
    # Add definitions as pure nodes first
    print("---- START: Add Definitions")
    for definition in self.definitions:
      print("Definition name: " + definition.semantic_data.name)

      try:
        new_node = GraphNode(
          definition.semantic_data, 
          NodeType.DEFINITION, 
          definition.base_path
        )
        self.graph.add_node(new_node)
      except NodeAlreadyExistsError as err:
        raise TextXSemanticError(f"Definition with name '{definition.semantic_data.name}' already exists.", **get_location(definition)) from err

    print("\nHandling Definition Dep Overrides")
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
            print("  - Copy: " + dep.def_name + " -> " + dep.assigned_name)

            node_to_copy = self.graph.get_node(dep.def_name)
            def_deep_copy = deep_copy_def(node_to_copy.definition)
            dep.apply_to(def_deep_copy)

            new_node = GraphNode(
              def_deep_copy, 
              NodeType.DEFINITION, 
              node_to_copy.base_path, 
              assigned_name=dep.assigned_name, 
              edges=node_to_copy.edges, 
              dep_edge_aliases=node_to_copy.dep_edge_aliases
            )
            self.graph.add_node(new_node)

    # Now add assigned nodes and edges
    for node_name in self.graph.get_nodes():
      node = self.graph.get_node(node_name)
      #print("Finding edges from: " + node.assigned_name)
      if node.definition.deps is not None:
        for dep_key in node.definition.deps.table:
          dep = node.definition.deps.table[dep_key]
          print("  - Dep: " + dep.assigned_name + " -> " + dep.def_name)
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
    
    print("---- END: Add Definitions\n\n")



  def add_instances(self):
    print("---- START: Add Instances")

    # Check instance creating order and get order
    chain_edges = []
    for _,v in self.other_instances.table.items():
      chain_edges.append((v.assigned_name, v.target_name))
    

    chains, problems = reverse_chains_allow_merges(chain_edges)
    if len(problems) > 0:
      raise TextXSemanticError(f"Detected loop or branhing of those instances and/or definitions: {problems[0]}")

    for chain in chains:
      #print(chain)
      for i in range(len(chain)-1):
        chain_base_node_name = chain[i]
        node_to_copy = self.graph.get_node(chain_base_node_name)
        if node_to_copy is None:
          raise TextXSemanticError(f"Definition '{chain_base_node_name}' for instance named '{chain[i+1]}' not found.")

        # Check if it is made in some previous chain
        next_node = self.graph.get_node(chain[i+1])
        if next_node is not None:
          continue

        # Make deep copy of definition
        def_deep_copy = deep_copy_def(node_to_copy.definition)
        other_instance_obj = self.other_instances.table[chain[i+1]]
        other_instance_obj.apply_to(def_deep_copy)

        # Make new node with deep copy
        print(" - Copy: " + other_instance_obj.target_name + " -> " + other_instance_obj.assigned_name)
        new_node = GraphNode(
          def_deep_copy, 
          NodeType.INSTANCE, 
          node_to_copy.base_path, 
          assigned_name=other_instance_obj.assigned_name, 
          edges=node_to_copy.edges,
          dep_edge_aliases=node_to_copy.dep_edge_aliases
        )
        self.graph.add_node(new_node)

    print("---- END: Add Instances\n\n")


  
    ############
    # Handle dep overrides separately
    # Find all dep override indicators
    print("---- START: Handling Instance Dep Overrides")
    for other_instance_key in self.other_instances.table:
      other_instance_obj = self.other_instances.table[other_instance_key]
      other_instance_node = self.graph.get_node(other_instance_key)
      print("Instance: " + other_instance_key)

      for dep_override_key in other_instance_obj.dep_overrides:
        print(" - Dep Override: " + dep_override_key)
        dep_override_node = self.graph.get_node(dep_override_key)

        if dep_override_node is None:
          raise TextXSemanticError(f"Instance for dependancy override '{dep_override_key}' not found.")
        
        # Find the nodes which need to be replaced
        # only if the node is present
        if hasattr(other_instance_node, "edges"):
          edges = list(other_instance_node.edges)
          for edge in edges:
            edge_node = self.graph.get_node(edge)
            if edge_node.definition.name == dep_override_node.definition.name:
              print(f"   - Replacing dep {edge_node.assigned_name} -> {dep_override_node.assigned_name}")
              self.graph.replace_edge(other_instance_node.assigned_name, edge_node.assigned_name, dep_override_node.assigned_name)
              
              print(f"   - Adding dep alias: ({dep_override_node.assigned_name} -> {edge_node.assigned_name})")
              other_instance_node.dep_edge_aliases[dep_override_node.assigned_name] = edge_node.assigned_name
          print("\n--------\n")
              


    ############
    # Add stack instance
    stack_node = self.graph.get_node("stack")
    stack_def_deep_copy = deep_copy_def(stack_node.definition)
    self.stack_instance.apply_to_stack_def(stack_def_deep_copy)


    new_stack_node = GraphNode(
      stack_def_deep_copy, 
      NodeType.INSTANCE, 
      stack_node.base_path, 
      assigned_name=self.stack_instance.stack_name, 
      edges=[]
    )
    self.graph.add_node(new_stack_node)

    # Add stack instance children as edges in graph
    for child in self.stack_instance.children:
      to_node = self.graph.get_node(child)
      if to_node is None:
        raise TextXSemanticError(f"Instance or definition with name '{child}' is not found.")
      self.graph.add_edge(new_stack_node, to_node)
      
    print("---- END: Handling Instance Dep Overrides\n\n")
