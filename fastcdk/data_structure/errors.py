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