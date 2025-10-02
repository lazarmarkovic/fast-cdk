

# This class represents a directed acyclic graph (DAG) for managing dependencies between FCDK definitions.








class FcdkDefSemantics:
  def __init__(self, fcdk_defs):
    self.definition_list = fcdk_defs
    self.global_dep_graph = DirectedAcyclicGraph()
    self.global_env_var_map = {}


  def kind(self, x): return x.__class__.__name__


  ##### Level of fcdk_defs!
  def make_global_dep_graph(self):
    nodes_with_deps = []

    #### Level of fcdk_defs!
    for fcdk_def in self.definition_list:
      new_node = GraphNode(fcdk_def, False)
      self.global_dep_graph.add_node(new_node)
      if len(fcdk_def.deps) > 0:
        nodes_with_deps.append(new_node)


    # Make all asignment nodes / nodes with custom assigned name / "instances of defs"
    ##### Level of fcdk_defs!
    for nwd in nodes_with_deps:
      for dep in nwd.definition.deps:
        if (dep.assigned_name != dep.def_name 
            and not self.global_dep_graph.node_exists(dep.assigned_name)
            and self.global_dep_graph.node_exists(dep.def_name)):

          print("Do it with: " +  dep.assigned_name)
          node_to_copy = self.global_dep_graph.get_node(dep.def_name)
          new_node = GraphNode(node_to_copy.definition, False, dep.assigned_name, dep.input, node_to_copy.edges)
          self.global_dep_graph.add_node(new_node)


    # Now add assigned nodes and edges
    #### Level of fcdk_defs!
    for nwd in nodes_with_deps:
      for dep in nwd.definition.deps:
        print("dep: " + dep.def_name + "  " + dep.assigned_name)
        if dep.assigned_name == dep.def_name:
          to_node = self.global_dep_graph.get_node(dep.def_name)
          if to_node is not None:
            self.global_dep_graph.add_edge(nwd, to_node)
          else:
            raise NodeNotFoundError(dep.def_name)

        elif self.global_dep_graph.node_exists(dep.assigned_name):
          to_node = self.global_dep_graph.get_node(dep.assigned_name)
          self.global_dep_graph.add_edge(nwd, to_node)
        
        else:
          pass
          # Not needed, it is handled above
          # new_node = GraphNode(fcdk_def, False, dep.assigned_name, dep.input)
          



  # Basic  algorithm ?
  ##### Level of fcdk!
  def add_instances(self, instances):
    stacks = []
    others = []
    for i in instances:
      print("Testing: " + self.kind(i) + "   " + i.assigned_name)
      if self.kind(i) == "StackInstanceInputs":
        stacks.append(i)
      elif self.kind(i) == "OtherInstanceInputs":
        others.append(i)

    
    for i in others:
      # now we need to find the GraphNode with this assigned node and add inputs to it
      # and then make a new graph node with all of this
      def_name = i.def_name
      node_to_copy = self.global_dep_graph.get_node(def_name)
      print("this one will be copied: " + node_to_copy.assigned_name)
      print("with new name: " + i.assigned_name)
      new_node = GraphNode(node_to_copy.definition, True, i.assigned_name, i.inputs, node_to_copy.edges)
      print("new node name: " + new_node.assigned_name)
      self.global_dep_graph.add_node(new_node)


    for i in stacks:
      def_name = i.def_name
      node_to_copy = self.global_dep_graph.get_node(def_name)
      new_node = GraphNode(node_to_copy.definition, True, i.assigned_name, i.inputs)
      self.global_dep_graph.add_node(new_node)
      print("\n\nChildren:")
      for c in i.children:
        print(c)
        # Needed, because fresh copy of basic stack def does not ever have any edges
        to_node = self.global_dep_graph.get_node(c)
        self.global_dep_graph.add_edge(new_node, to_node)


    


