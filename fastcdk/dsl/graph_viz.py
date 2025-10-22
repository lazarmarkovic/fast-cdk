import networkx as nx
from pyvis.network import Network


class InteractiveDAG:
    def __init__(self, nodes=None, edges=None):
        self.G = nx.DiGraph()
        if nodes: self.G.add_nodes_from(nodes)
        if edges:
            for u, v in edges:
                self.G.add_edge(u, v)
                if not nx.is_directed_acyclic_graph(self.G):
                    self.G.remove_edge(u, v)
                    raise ValueError(f"edge {u}->{v} creates a cycle")

    def show(self, html_path="graph_viz.html"):
        net = Network(
            height="750px", width="100%",
            directed=True, notebook=False
        )
        # build graph
        for n in self.G.nodes:
            net.add_node(n, label=str(n), size=25)
        for u, v in self.G.edges:
            net.add_edge(u, v)

        # **turn off physics** so nodes never auto-move
        net.toggle_physics(False)

        # optional UI so you could re-enable it by hand
        net.show_buttons(filter_=['physics'])

        # write out static-physics HTML
        net.write_html(html_path, open_browser=False, notebook=False)
        print(f"open {html_path} → drag nodes, they’ll stay where you put ’em")
