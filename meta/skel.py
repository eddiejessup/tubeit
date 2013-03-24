import random
import json
import numpy as np
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as pp

prop = fm.FontProperties(fname='London-Tube.ttf', size='small')

np.random.seed(115)

line_deets = {
    'baker': ('Bakerloo', 'brown'),
    'cent': ('Central', '#fe5806'),
    'circ': ('Circle', 'yellow'),
    'dist': ('District', '#00c131'),
    'elond': ('East London', 'orange'),
    'ham': ('Hammersmith & City', '#ff9cb6'),
    'jub': ('Jubilee', 'gray'),
    'metro': ('Metropolitan', 'purple'),
    'north': ('Northern', 'black'),
    'picc': ('Piccadilly', 'blue'),
}

class Network(object):
    def __init__(self):
        self.lines = []

    def get_n_verts(self, node):
        n_verts = 0
        for line in self.lines:
            if line.in_line(node): n_verts += 1
        return n_verts

    def in_network(self, node):
        return self.get_n_verts(node) > 0

    def n_lines(self, node1, node2):
        return sum([l.are_connected(node1, node2) for l in self.lines])

    def is_junction(self, node):
        return sum([l.in_line(node) for l in self.lines]) > 1

    def simplify(self, n=10):
        for _ in range(n):
            for line in self.lines:
                line.simplify()

    def add_line(self, line):
        if line not in self.lines: self.lines.append(line)
        else: raise Exception

    def jsonable(self):
        return [l.jsonable() for l in self.lines]

class Line(object):
    def __init__(self, label, color):
        self.label = label
        self.color = color
        self.nodes = []

    def extend(self, node):
        self.nodes.append(node)

    def end(self):
        return self.nodes[-1]

    def start(self):
        return self.lines[0]

    def in_line(self, node):
        return node in self.nodes

    def simplify(self):
        for i in range(len(self.nodes) - 1):
            self.nodes[i].simplify(self.nodes[i + 1])

    def are_connected(n1, n2):
        return max([self.nodes[i] in [n1, n2] and self.nodes[i + 1] in [n1, n2] for i in range(len(self.nodes) - 1)])

    def next(self, node):
        for i in range(len(self.nodes) - 1):
            if self.nodes[i] is node: return self.nodes[i + 1]
        if self.nodes[-1] is node: return node
        raise Exception

    def jsonable(self):
        return {'label': self.label,
                'nodes': [n.jsonable() for n in self.nodes]}

class Node(object):
    def __init__(self, r, label=''):
        self.r = r
        self.label = label

    def get_sep(self, node):
        return np.sqrt(np.sum(np.square(self.r - node.r)))

    def simplify(self, node):
        thetas = np.linspace(-np.pi, np.pi, 9)
        v = node.r - self.r
        theta = np.arctan2(v[1], v[0])
        theta_s = thetas[np.abs(thetas - theta).argmin()]
        node.r = self.r + np.array([np.cos(theta_s), np.sin(theta_s)]) * np.sqrt(np.sum(np.square(v)))

    def jsonable(self):
        return {'label': self.label,
                'r': [self.r[0], self.r[1]]}

def ComplexHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))

def make_points():
    rs = np.zeros([n_nodes, d])
    for i in range(len(rs)):
        while True:
            rs[i, 0] = np.random.normal(loc=x_mid, scale=x_range)
            rs[i, 1] = np.random.normal(loc=y_mid, scale=y_range)
            valid = True
            if not x_min < rs[i, 0] < x_max: valid = False
            if not y_min < rs[i, 1] < y_max: valid = False
            if rs[i, 0] < 0.35 and rs[i, 1] < 0.12: valid = False
            if i > 0 and np.sqrt(np.sum(np.square(rs[i] - rs[:i]), axis=-1)).min() < r_sep_min: valid = False
            if valid: break
    return rs

def make_nodes(rs):
    nodes = []
    for i in range(len(rs)):
        nodes.append(Node(rs[i]))
    return nodes

def make_network(nodes):
    network = Network()
    for line_key in line_deets:
        line = Line(*line_deets[line_key])
        line.extend(random.choice(nodes))
        for _ in range(n_stops):
            R = [line.end().get_sep(node) for node in nodes]
            for i in np.argsort(R):
                valid = True
                if line.in_line(nodes[i]): valid = False
                # TODO: if vert.n_lines() >= shared_vert_max: valid = False
                if valid:
                    line.extend(nodes[i])
                    break
        network.add_line(line)
    return network

def plot(network, fname='out'):
    fig = pp.figure()
    ax = fig.gca()
    ax.set_aspect('equal')
    ax.set_xlim([-x_buff, x_max+x_buff])
    ax.set_ylim([-y_buff, y_max+y_buff])

    pp.grid(True, color='#4ac6ff', linestyle='-')
    pp.xticks(np.arange(0.0, 0.901, 0.1))
    pp.yticks(np.arange(0.0, 0.601, 0.1))

    nodes_plot = []
    for line in network.lines:
        for node in line.nodes:
            if node not in nodes_plot:
                nodes_plot.append(node)
                if network.is_junction(node): c = mpl.patches.Circle(node.r, radius=0.005, fc='white', ec='black', lw=2, zorder=10)
                else: c = mpl.patches.Circle(node.r, radius=0.003, fc='black', lw=0, zorder=10)
                ax.add_patch(c)

            node_next = line.next(node)
            if node_next is not node:
                r = np.array([node_next.r, node.r])
                l = mpl.lines.Line2D(r[:, 0], r[:, 1], color=line.color)
                ax.add_line(l)

#    pp.show()
    pp.savefig('%s.png' % fname)

# Point generation
r_sep_min = 0.05
x_min = 0.0
y_min = 0.0
x_max = 0.9
y_max = 0.6
x_mid = (x_min + x_max) / 2.0
y_mid = (y_min + y_max) / 2.0
x_range = x_max - x_min
y_range = y_max - y_min
x_buff = x_range / 20.0
y_buff = y_range / 20.0

# Map generation
d = 2
n_nodes = 100
n_lines = 10
n_stops = 30

print('Making points')
rs = make_points()
print('Making nodes')
nodes = make_nodes(rs)
print('Making network')
network = make_network(nodes)
d = json.dumps(network, default=ComplexHandler)
print(d)
#print('Plotting')
#for i in range(10):
#    plot(network, i)
#    network.simplify(1)