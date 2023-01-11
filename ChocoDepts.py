import tkinter
from xml.etree import ElementTree
from tkinter import Tk, Canvas, Frame, BOTH, ALL, CENTER
import glob
import random


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
            matches = [n for n in nodes if n.id.lower() == identifier.lower()]
            if len(matches) == 1:
                return matches[0]
            print("dependency {} not found/installed/unique!".format(identifier))

        for node in nodes:
            self.canvas.create_text(node.coordinate.x, node.coordinate.y, font="Sans 12", text=node.label,
                                    justify=CENTER)
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

        paths = glob.glob('C:\\ProgramData\\chocolatey\\lib\\*\\*.nuspec')
        for path in paths:
            dom = ElementTree.parse(path)
            root = dom.getroot()
            namespace = root.tag.split('}')[0].strip('{')

            identifier = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}id'.format(namespace)).text
            node = Node(identifier)
            # TODO add linebreak if label is longer than N chars
            node.label = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}title'.format(namespace)).text
            dependencies = dom.find('{{{}}}metadata'.format(namespace)).find('{{{}}}dependencies'.format(namespace))
            if dependencies:
                for dependency in dependencies.findall('{{{}}}dependency'.format(namespace)):
                    # TODO question whether id string or reference should be used:
                    #  i.e. create placeholder using only the identifier if a node doesnt exist.
                    #  then reference the new node. this approach allows to color dead dependencies
                    #  (those who have no attributes but the identifier, which should never happen so it's pointless?!)
                    dependency_id = dependency.attrib.get('id')
                    node.dependencies.append(dependency_id)
            self.nodes.append(node)

    def update_node_locations(self):
        # TODO order nodes by using dependencies as neighbors and assigning matching coordinates
        for node in self.nodes:
            node.coordinate = Coordinate(random.randint(10, 700), random.randint(10, 300))

    def get_nodes(self):
        self.read_nodes_from_xml()
        self.update_node_locations()
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
    root.title("ChocoDepts")
    root.mainloop()


if __name__ == '__main__':
    main()
