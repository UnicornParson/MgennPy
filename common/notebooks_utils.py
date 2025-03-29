from IPython.display import JSON
from IPython.display import Markdown
import matplotlib.pyplot as plt
import networkx as nx
import json
from pyvis.network import Network
from IPython.display import display, HTML

class PackageUIHelper():
    @staticmethod
    def showGraph(pkg, link_to_zero = False):
        #net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=True, directed =True)

        ZH = "ZERO_HOLE"
        def hasNode(nodes, key)->bool:
            for node in nx_graph.nodes:
                if str(node) == str(key):
                    return True
            return False
        nx_graph = nx.DiGraph()

        for n in pkg.neurons:
            nx_graph.add_node(str(n["id"]), size = 10 + int(float(n["currentEnergy"])), title=('neuron %d' % n["id"]), group=1)
        for o in pkg.outputs:
            nx_graph.add_node(str(o["id"]), size = 10, title=('outputs %d' % n["id"]), group=2)
        for i in pkg.inputs:
            nx_graph.add_node(str(i["name"]), size = 5, title=('input %s' % i["name"]), group=3)

        #make direct links
        nx_graph.add_node(str(ZH), size = 1, title=("missed node"), group=1)
        if pkg.links:
            l = pkg.links[1]
            start, stop = pkg.linkEnds(l)
            for l in pkg.links:
                start, stop = pkg.linkEnds(l)
                link_len = int(l['length'])
                print("link ", start, " to " , str(stop), " sz:", link_len)
                if not start:
                    if link_to_zero:
                        nx_graph.add_edge(ZH, stop, length = (link_len + 1), weight=(link_len + 1))
                    continue
                if not hasNode(nx_graph.nodes, str(stop)):
                    if link_to_zero:
                        nx_graph.add_edge(ZH, stop, value = (link_len + 1), weight=(link_len + 1))
                    continue
                nx_graph.add_edge(str(start), str(stop), length = (link_len + 1), weight=(link_len + 1) )

        for n in pkg.neurons:
            for rc in n['receivers']:
                if not pkg.isLink(rc):
                    nx_graph.add_edge(str(n["id"]), str(rc), length = 1, weight = 1)
        nt.from_nx(nx_graph)
        return nt.show('nx.html')
