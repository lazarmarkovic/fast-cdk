class NodeAlreadyExistsError(Exception):
  def __init__(self, node_name):
    super().__init__(f"Node '{node_name}' already exists in the graph.")
    self.node_name = node_name

class NodeNotFoundError(Exception):
  def __init__(self, node_name):
    super().__init__(f"Node '{node_name}' not found in the graph.")
    self.node_name = node_name

class GraphCycleError(Exception):
  def __init__(self, node1_name, node2_name):
    super().__init__(f"Graph cycle detected between '{node1_name}' and '{node2_name}'.")
    self.node1_name = node1_name
    self.node2_name = node2_name

# This class represents a directed acyclic graph (DAG) for managing dependencies between FCDK definitions.
class GraphNode:
  def __init__(self, definition, is_instance, assigned_name=None, input_override=None, edges=None):
    self.is_instance = is_instance
    self.edges = []
    self.definition = definition
    self.assigned_name = assigned_name if assigned_name is not None else definition.name
    self.input_override = input_override
    if edges is not None:
      for e in edges:
        self.edges.append(e)


class DirectedAcyclicGraph:
  def __init__(self):
    self.graph = {}


  def add_node(self, graph_node):
    if graph_node.assigned_name not in self.graph:
      self.graph[graph_node.assigned_name] = graph_node 
    else:
      raise NodeAlreadyExistsError(graph_node.assigned_name)


  def add_edge(self, from_node, to_node):
    if self.graph[from_node.assigned_name] is None:
      raise NodeNotFoundError(from_node.assigned_name)
    if self.graph[to_node.assigned_name] is None:
      raise NodeNotFoundError(to_node.assigned_name)
    # Add edge if it doesn't create a cycle
    if not self._would_create_cycle(from_node.assigned_name, to_node.assigned_name):
      self.graph[from_node.assigned_name].edges.append(to_node.assigned_name)
    else:
      raise GraphCycleError(from_node.assigned_name, to_node.assigned_name)


  def _would_create_cycle(self, from_name: str, to_name: str) -> bool:
    # trivial self-loop
    if from_name == to_name:
      return True

    # if the “to” node doesn’t even exist yet, no cycle
    if to_name not in self.graph:
      return False

    visited = set()

    def dfs(current: str) -> bool:
      if current == from_name:
        return True
      visited.add(current)
      for nbr in self.graph[current].edges:  # noqa: SIM110
        if nbr not in visited and dfs(nbr):
          return True
      return False

    # if you can reach `from_name` starting at `to_name`, adding from→to closes the loop
    return dfs(to_name)


  def get_nodes(self):
    return list(self.graph.keys())


  def get_edges(self):
    edges = []
    for from_node_name in self.graph:
      #print(from_node_name)
      for to_node_name in self.graph[from_node_name].edges:
        #print("--- " + to_node_name)
        edges.append((from_node_name, to_node_name))
    return edges


  def node_exists(self, node_name):
    return node_name in self.graph


  def get_node(self, node_name):
    if node_name in self.graph:
      return self.graph[node_name]
    else:
      return None




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


    


