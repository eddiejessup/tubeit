import random
import json
import numpy as np
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as pp

#prop = fm.FontProperties(fname='London-Tube.ttf', size='small')

np.random.seed(115)

class Network(object):
    d = 2
    line_deets = (('Bakerloo', 'brown'),
                  ('Central', '#fe5806'),
                  ('Circle', 'yellow'),
                  ('District', '#00c131'),
                  ('East London', 'orange'),
                  ('Hammersmith & City', '#ff9cb6'),
                  ('Jubilee', 'gray'),
                  ('Metropolitan', 'purple'),
                  ('Northern', 'black'),
                  ('Piccadilly', 'blue'),
                  )

    def __init__(self, n_stops):
        self.n_stops = n_stops
        self.lines = []

    def n_verts(self, node):
        return sum([l.in_line(node) for l in self.lines])

    def n_lines(self, node1, node2):
        return sum([l.are_connected(node1, node2) for l in self.lines])

    def in_network(self, node):
        return self.n_verts(node) > 0

    def is_stop(self, node):
        return self.n_verts(node) == 1

    def is_junction(self, node):
        return self.n_verts(node) > 1

    def is_terminus(self, node):
        return max([l.is_terminus(node) for l in self.lines])

    def simplify(self):
        for l in self.lines: l.simplify()

    def add_line(self, line):
        if line not in self.lines: self.lines.append(line)
        else: raise Exception

    def jsonable(self):
        return [l.jsonable() for l in self.lines]

    def nodes_to_lines(self, nodes):
        for line_deet in self.line_deets:
            line = Line(*line_deet)
            line.extend(nodes[np.random.randint(len(nodes))])
            for _ in range(self.n_stops):
                R = [line.end().get_sep(node) for node in nodes]
                for i in np.argsort(R):
                    valid = True
                    if line.in_line(nodes[i]): valid = False
                    if self.n_lines(line.end(), nodes[i]) > 1: valid = False
                    if valid:
                        line.extend(nodes[i])
                        break
            self.add_line(line)

    def plot(self):
        fig = pp.figure()
        ax = fig.gca()
        ax.set_aspect('equal')
        ax.set_xlim([-0.1, 1.1])
        ax.set_ylim([-0.1, 1.1])

        pp.grid(True, color='#4ac6ff', linestyle='-')
        pp.xticks(np.arange(0.0, 1.01, 0.1))
        pp.yticks(np.arange(0.0, 1.01, 0.1))

        nodes_plot = []
        for line in self.lines:
            for node in line.nodes:
                if node not in nodes_plot:
                    nodes_plot.append(node)
                    if self.is_junction(node): c = mpl.patches.Circle(node.r, radius=0.005, fc='white', ec='black', lw=2, zorder=10)
                    else: c = mpl.patches.Circle(node.r, radius=0.003, fc='black', lw=0, zorder=10)
                    ax.add_patch(c)

                node_next = line.next(node)
                if node_next is not node:
                    r = np.array([node_next.r, node.r])
                    l = mpl.lines.Line2D(r[:, 0], r[:, 1], color=line.color)
                    ax.add_line(l)

        pp.show()
    #    pp.savefig('%s.png' % fname)

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

    def is_terminus(self, node):
        return node in [self.nodes[0], self.nodes[-1]]

    def simplify(self):
        for i in range(len(self.nodes) - 1): self.nodes[i].simplify(self.nodes[i + 1])

    def are_connected(self, n1, n2):
        return max([self.nodes[i] in [n1, n2] and self.nodes[i + 1] in [n1, n2] for i in range(len(self.nodes) - 1)])

    def next(self, node):
        for i in range(len(self.nodes) - 1):
            if self.nodes[i] is node: return self.nodes[i + 1]
        if self.nodes[-1] is node: return node
        raise Exception

    def jsonable(self):
        return {'label': self.label, 'nodes': [n.jsonable() for n in self.nodes]}

class Node(object):
    thetas = np.linspace(-np.pi, np.pi, 9)

    def __init__(self, r, label=''):
        self.r = r
        self.label = label

    def get_sep(self, node):
        return np.sqrt(np.sum(np.square(node.r - self.r)))

    def simplify(self, node):
        v = node.r - self.r
        theta_s = self.thetas[np.abs(self.thetas - np.arctan2(v[1], v[0])).argmin()]
        node.r = self.r + np.array([np.cos(theta_s), np.sin(theta_s)]) * np.sqrt(np.sum(np.square(v)))

    def jsonable(self):
        return {'label': self.label, 'r': [self.r[0], self.r[1]]}

def ComplexHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))

def make_points(n, r_sep_min):
    rs = np.zeros([n, 2])
    for i in range(len(rs)):
        while True:
            rs[i] = np.random.normal(loc=0.5, size=2)
            valid = True
            if not 0.0 < rs[i, 0] < 1.0: valid = False
            if not 0.0 < rs[i, 1] < 1.0: valid = False
            if i > 0 and np.sqrt(np.sum(np.square(rs[i] - rs[:i]), axis=-1)).min() < r_sep_min: valid = False
            if valid: break
    return rs

def main():
    n_nodes = 100
    r_sep_min = 0.05
    n_stops = 20

    network = Network(n_stops)
    print('Making nodes')
    nodes = [Node(r) for r in make_points(n_nodes, r_sep_min)]
    print('Making network')
    network.nodes_to_lines(nodes)
    print('Simplifying nodes')
    for _ in range(1):
        network.simplify()
    print('Dumping to JSON')
    d = json.dump(network, open('map.json', 'w'), default=ComplexHandler)
    print('Plotting')
    network.plot()
    print('Done')

if __name__ == '__main__': main()