from enum import Enum

from fastcdk.data_structure.errors import GraphCycleError, NodeAlreadyExistsError, NodeNotFoundError


class NodeType(Enum):
  DEFINITION = 0
  INSTANCE = 1



class GraphNode:
  def __init__(self, definition, node_type, instance=None, assigned_name=None, edges=None):
    self.type: NodeType = node_type
    self.edges: list[GraphNode] = []
    self.definition = definition
    self.instance = instance
    self.assigned_name = assigned_name if assigned_name is not None else definition.name

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
    if not self._would_create_cycle(from_node.assigned_name, to_node.assigned_name):
      self.graph[from_node.assigned_name].edges.append(to_node.assigned_name)
    else:
      raise GraphCycleError(from_node.assigned_name, to_node.assigned_name)


  def _would_create_cycle(self, from_name: str, to_name: str) -> bool:
    if from_name == to_name:
      return True

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
    
    return dfs(to_name)


  def get_nodes(self):
    return list(self.graph.keys())


  def get_edges(self):
    edges = []
    for from_node_name in self.graph:
      for to_node in self.graph[from_node_name].edges:
        edges.append((from_node_name, to_node))
    return edges


  def node_exists(self, node_name):
    return node_name in self.graph


  def get_node(self, node_name):
    if node_name in self.graph:
      return self.graph[node_name]
    else:
      return None


  def replace_edge(self, from_node_name: str, old_to_node_name: str, new_to_node_name: str):
    if not self.node_exists(from_node_name):
      raise NodeNotFoundError(from_node_name)
    if not self.node_exists(old_to_node_name):
      raise NodeNotFoundError(old_to_node_name)
    if not self.node_exists(new_to_node_name):
      raise NodeNotFoundError(new_to_node_name)

    from_node = self.graph[from_node_name]
    if old_to_node_name in from_node.edges:
      from_node.edges.remove(old_to_node_name)
      from_node.edges.append(new_to_node_name)
    else:
      raise NodeNotFoundError(f"Edge from {from_node_name} to {old_to_node_name} does not exist.")