import glob
import math
import os
import re
import tkinter
from operator import attrgetter
from tkinter import Tk, Canvas, Frame, BOTH, ALL, CENTER
from defusedxml import ElementTree

from colour import Color


def draw_arrow(canvas, from_x, from_y, to_x, to_y):
    margin = 70

    x_abs = abs(to_x - from_x)
    y_abs = abs(to_y - from_y)

    x_margin = margin / (x_abs + y_abs) * x_abs
    y_margin = margin / (y_abs + x_abs) * y_abs

    if x_abs > 0:
        x_direction_correction_factor = (to_x - from_x) / abs(to_x - from_x)
        to_x -= x_margin * x_direction_correction_factor
        from_x += x_margin * x_direction_correction_factor

    if y_abs > 0:
        y_direction_correction_factor = (to_y - from_y) / abs(to_y - from_y)
        to_y -= y_margin * y_direction_correction_factor
        from_y += y_margin * y_direction_correction_factor

    canvas.create_line(from_x, from_y, to_x, to_y, arrow=tkinter.LAST)


class ChocoDepts(Frame):

    def __init__(self):
        super().__init__()

        # init ui
        self.canvas = Canvas(self)
        self.init_canvas()
        self.pack(fill=BOTH, expand=1)

    def do_zoom(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        factor = 1.001 ** event.delta
        self.canvas.scale(ALL, x, y, factor, factor)

    def init_canvas(self):
        self.canvas.bind("<MouseWheel>", self.do_zoom)
        self.canvas.bind('<ButtonPress-1>', lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B1-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
        self.canvas.pack(fill=BOTH, expand=1)

    def draw_directed_graph(self, nodes):

        def get_node_by_id(identifier):
            matches = [n for n in nodes if n.id == identifier]
            if len(matches) == 1:
                return matches[0]
            print("dependency {} not found/installed/unique!".format(identifier))

        # prepare color palette
        max_connection_count = max(node.connection_count for node in nodes)
        red = Color("green")
        colors = list(red.range_to(Color("red"), max_connection_count + 1))

        for node in nodes:
            font = "Sans 12 bold underline" if node.is_leaf else "Sans 12"
            self.canvas.create_text(node.coordinate.x, node.coordinate.y, fill=colors[node.connection_count],
                                    font=font, text=node.label, justify=CENTER)
            for dependency in node.dependencies:
                dependency_node = get_node_by_id(dependency)
                if dependency_node:
                    draw_arrow(self.canvas, node.coordinate.x, node.coordinate.y, dependency_node.coordinate.x,
                               dependency_node.coordinate.y)


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

            dependencies = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}dependencies'.format(namespace))
            if dependencies:
                for dependency in dependencies.findall('{{{}}}dependency'.format(namespace)):
                    dependency_id = dependency.attrib.get('id').lower()
                    node.dependencies.append(dependency_id)
            self.nodes.append(node)

    def order_nodes_by_dependency_count(self):
        # add connection count
        for node in self.nodes:
            node.connection_count = 0

            # outgoing
            node.connection_count += len(node.dependencies)

            # incoming
            node.is_leaf = True
            for other_node in self.nodes:
                if node == other_node:
                    continue
                for dependency in other_node.dependencies:
                    if dependency == node.id:
                        node.connection_count += 1
                        node.is_leaf = False
        # sort
        self.nodes.sort(key=attrgetter('connection_count'), reverse=True)

    def update_node_locations(self):
        # spiral parameters depend on number of nodes
        node_count = len(self.nodes)
        vert_spacing = 10 * node_count
        horz_spacing = 10 * node_count
        theta_max = node_count * math.pi

        # constants
        b = vert_spacing / 2 / math.pi
        smax = 0.5 * b * theta_max * theta_max

        for i in range(len(self.nodes)):
            s = (smax / horz_spacing) * i
            theta_i = math.sqrt(2 * s / b)
            xi = b * theta_i * math.cos(theta_i)
            yi = b * theta_i * math.sin(theta_i)

            self.nodes[i].coordinate = Coordinate(xi, yi)

    def update_node_labels(self):
        for node in self.nodes:
            node.label = re.sub("(.{15})", "\\1\n", node.label, 0, re.DOTALL)

    def get_nodes(self):
        self.read_nodes_from_xml()
        self.order_nodes_by_dependency_count()
        self.update_node_locations()
        self.update_node_labels()
        return self.nodes


def main():
    root = Tk()

    cd = ChocoDepts()
    nn = NuspecToNodes()
    nodes = nn.get_nodes()
    cd.draw_directed_graph(nodes)

    window_width = 800
    window_height = 600
    x_coordinate = int((root.winfo_screenwidth() / 2) - (window_width / 2))
    y_coordinate = int((root.winfo_screenheight() / 2) - (window_height / 2))
    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_coordinate, y_coordinate))
    root.title("ChocoDepts v0.0.1")
    root.mainloop()


if __name__ == '__main__':
    main()
