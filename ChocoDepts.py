import glob
import os
import re

import webview
from colour import Color
from defusedxml import ElementTree
from pyvis.network import Network


def draw_directed_graph(graph, nodes):
    def get_node_by_id(identifier):
        matches = [n for n in nodes if n.id == identifier]
        if len(matches) == 1:
            return matches[0]
        print("dependency {} not found/installed/unique!".format(identifier))

    # prepare color palette
    max_connection_count = max(node.connection_count for node in nodes)
    red = Color("#00FF00")
    colors = list(red.range_to(Color("#FF0000"), max_connection_count + 1))

    for node in nodes:
        graph.add_node(node.label, color=colors[node.connection_count].hex, title=node.version)
        # font = "Sans 12 bold underline" if node.is_leaf else "Sans 12"

    for node in nodes:
        for dependency in node.dependencies:
            dependency_node = get_node_by_id(dependency)
            if dependency_node:
                graph.add_edge(node.label, dependency_node.label, color='black')


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Node:
    def __init__(self, identifier):
        self.id = identifier
        self.coordinate = Coordinate(0, 0)
        self.label = ""
        self.dependencies = []


class NuspecToNodes:

    def __init__(self):
        self.nodes = []

    def read_nodes_from_xml(self):
        install_dir = os.environ['ChocolateyInstall']
        regex = os.path.join(install_dir, 'lib', '*', '*.nuspec')
        paths = glob.glob(regex)
        for path in paths:
            try:
                dom = ElementTree.parse(path)
            except SyntaxError as se:
                raise se
            root = dom.getroot()
            namespace = root.tag.split('}')[0].strip('{')

            identifier = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}id'.format(namespace)).text.lower()
            node = Node(identifier)
            node.label = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}title'.format(namespace)).text
            node.version = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}version'.format(namespace)).text

            dependencies = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}dependencies'.format(namespace))
            if dependencies:
                for dependency in dependencies.findall('{{{}}}dependency'.format(namespace)):
                    dependency_id = dependency.attrib.get('id').lower()
                    node.dependencies.append(dependency_id)
            self.nodes.append(node)

    def annotate_nodes_by_relations(self):
        for node in self.nodes:
            node.connection_count = 0
            node.connection_count += len(node.dependencies)
            node.is_leaf = True
            for other_node in self.nodes:
                if node == other_node:
                    continue
                for dependency in other_node.dependencies:
                    if dependency == node.id:
                        node.connection_count += 1
                        node.is_leaf = False

    def update_node_labels(self):
        for node in self.nodes:
            node.label = re.sub("(.{15})", "\\1\n", node.label, 0, re.DOTALL)

    def get_nodes(self):
        self.read_nodes_from_xml()
        self.annotate_nodes_by_relations()
        self.update_node_labels()
        return self.nodes


class Main:
    def __init__(self):
        nn = NuspecToNodes()
        self.nodes = nn.get_nodes()

        self.g = Network(width='100%', height='550px')
        self.g.toggle_physics(True)

        self.window = webview.create_window('ChocoDepts v0.0.1', html='Loading', width=800, height=600)
        self.window.events.resized += self.on_resized

        def load_html(window):
            self.update_html()

        webview.start(load_html, self.window)

    def update_html(self):
        draw_directed_graph(self.g, self.nodes)
        html = self.g.generate_html('chocodepts.html')
        self.window.load_html(html)

    def on_resized(self, width, height):
        self.g.width = '100%'
        self.g.height = height - 50
        self.update_html()


if __name__ == '__main__':
    Main()
