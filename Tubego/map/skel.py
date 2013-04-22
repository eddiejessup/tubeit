import json
import numpy as np
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as pp
import metro
import potentials
import utils

np.random.seed(116)

def dedupe(a):
    b = []
    for e in a:
        if e not in b: b.append(e)
    return b

class Network(object):
    d = 2
    n_stops = 10

    def __init__(self, nodes):
        self.nodes = nodes
        self.paths = []

        def node_valid(path, node):
            # Stop paths passing through themselves
            if path.node_in_path(node): return False
            # Restrict number of neighbours (distinct nodes from which node can be reached)
            if len(self.neighbs(node)) > 3: return False
            # Restrict number of redundant vertices (distinct paths to get to node from current node)
            if len(self.get_paths_vert(Vertex(path.end(), node))) > 1: return False
            # Restrict number of redundant nodes (distinct paths to arrive at node from any node)
            if len(self.get_paths_node(node)) > 3: return False
            # Leave termina as they are
            if len(self.neighbs(node)) == 1: return False
            return True

        def make_node_list(path):
            if path.end() is None:
                nodes_sort = []
                for node in self.nodes:
                    if not self.in_network(node): nodes_sort.append(node)
                np.random.shuffle(nodes_sort)
            else:
                inds = np.argsort([path.end().get_sep(node) for node in self.nodes])
                nodes_sort = [self.nodes[i] for i in inds]
            return nodes_sort

        while len(self.nodes_in_network()) < len(self.nodes):
            path = Path()
            i_since_change = 0
            while i_since_change < 1000:
                for node in make_node_list(path):
                    if node_valid(path, node):
                        path.extend(node)
                        i_since_change = 0
                        break
                if len(path.nodes) > self.n_stops:
                    break
                i_since_change += 1
            self.paths.append(path)

    def in_network(self, node):
        return node in self.nodes_in_network()

    def is_connected(self, node):
        return len(self.neighbs(node)) > 0

    def is_terminus(self, node):
        return len(self.neighbs(node)) == 1

    def is_stop(self, node):
        return len(self.neighbs(node)) == 2

    def is_junction(self, node):
        return len(self.neighbs(node)) > 2

    def nodes_in_network(self):
        ns = []
        for p in self.paths: ns += p.nodes
        return dedupe(ns)

    def neighbs(self, node):
        neighbs = []
        for p in self.paths:
            if p.node_in_path(node):
                neighbs += p.neighbs(node)
        return dedupe(neighbs)

    def get_paths_node(self, n):
        ps = []
        for p in self.paths:
            if p.node_in_path(n): ps.append(p)
        return ps

    def get_paths_vert(self, v):
        ps = []
        for p in self.paths:
            if p.vert_in_path(v): ps.append(p)
        return ps

    def simplify(self):
        for p in np.random.permutation(self.paths): p.simplify()

    def plot(self, fname=None):
        fig = pp.figure()
        ax = fig.gca()
        ax.set_aspect('equal')
        ax.set_xlim([-0.1, 1.1])
        ax.set_ylim([-0.1, 1.1])

        ax.grid(True, color='#4ac6ff', linestyle='-')
        ax.set_xticks(np.arange(0.0, 1.01, 0.1))
        ax.set_yticks(np.arange(0.0, 1.01, 0.1))

        for node in self.nodes:
            if self.is_junction(node):
                c = mpl.patches.Circle(node.r, radius=0.005, fc='white', ec='black', lw=2, zorder=10)
            else:
                if self.is_stop(node):
                    c = mpl.patches.Circle(node.r, radius=0.0075, fc='blue', lw=0, zorder=10)
                elif self.is_terminus(node):
                    c = mpl.patches.Circle(node.r, radius=0.015, fc='green', lw=0, zorder=10)
                else:
                    raise Exception
            ax.add_patch(c)

        def n_paths_vert_so_far(v):
            return sum([v.equiv(v1) for v1 in verts_used])

        verts_used = []
        for p in self.paths:
            for i in range(len(p.nodes) - 1):
                v = Vertex(p.nodes[i], p.nodes[i + 1])
                r = v.r_offset(0.007 * n_paths_vert_so_far(v))
                verts_used.append(v)
                l = mpl.lines.Line2D(r[:, 0], r[:, 1], color='black', lw=3)
                ax.add_line(l)

        if fname is None: pp.show()
        else: fig.savefig('%s.png' % fname)

    def jsonable(self):
        return [p.jsonable() for p in self.paths]

class Path(object):
    def __init__(self, label=''):
        self.label = label
        self.nodes = []

    def extend(self, node):
        self.nodes.append(node)

    def end(self):
        if len(self.nodes) > 0: return self.nodes[-1]
        else: return None

    def start(self):
        if len(self.nodes) > 0: return self.nodes[0]
        else: return None

    def vert_in_path(self, v):
        return max([v.equiv(v1) for v1 in self.to_verts()])

    def node_in_path(self, node):
        return node in self.nodes

    def is_terminus(self, node):
        return node in [self.nodes[0], self.nodes[-1]]

    def to_verts(self, direction=1):
        vs = []
        if direction == 1:
            for i in range(len(self.nodes) - 1):
                vs.append(Vertex(self.nodes[i], self.nodes[i + 1]))
        elif direction == -1:
            for i in range(len(self.nodes) - 1, -1, -1):
                vs.append(Vertex(self.nodes[i], self.nodes[i - 1]))
        else:
            raise Exception
        return vs

    def neighbs(self, node):
        return [n for n in [self.next(node), self.prev(node)] if n is not None]

    def node_to_i(self, node):
        for i in range(len(self.nodes)):
            if self.nodes[i] is node: return i
        raise Exception

    def next(self, node):
        i = self.node_to_i(node)
        if i < len(self.nodes) - 1: return self.nodes[i + 1]
        else: return None

    def prev(self, node):
        i = self.node_to_i(node)
        if i > 0: return self.nodes[i - 1]
        else: return None

    def simplify(self):
        for v in self.to_verts(direction=2*np.random.randint(2) - 1): v.simplify()

    def jsonable(self):
        return {'label': self.label, 'nodes': [n.jsonable() for n in self.nodes]}

class Node(object):
    def __init__(self, r, label=''):
        self.r = r
        self.label = label

    def get_sep(self, node):
        return np.sqrt(np.sum(np.square(node.r - self.r)))

    def jsonable(self):
        return {'label': self.label, 'r': [self.r[0], self.r[1]]}

class Vertex(object):
    r_sep_min = 0.05
    thetas = np.linspace(-np.pi, np.pi, 9)

    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2

    def nodes(self):
        return (self.node1, self.node2)

    def v(self):
        return self.node2.r - self.node1.r

    def u(self):
        v = self.v()
        return v / np.sqrt(np.sum(np.square(v)))

    def u_perp(self):
        u = self.u()
        return np.array([u[1], -u[0]])

    def offset(self, d):
        return d * self.u_perp()

    def r(self):
        return np.array([self.node1.r, self.node2.r])

    def r_offset(self, d):
        return self.r() + self.offset(d)

    def equiv(self, v):
        return v.node1 in self.nodes() and v.node2 in self.nodes()

    def simplify(self):
        v = self.v()
        theta_s = self.thetas[np.abs(self.thetas - np.arctan2(v[1], v[0])).argmin()]
        u = np.array([np.cos(theta_s), np.sin(theta_s)])
        mag = np.maximum    (np.sqrt(np.sum(np.square(v))), self.r_sep_min)
        self.node2.r = self.node1.r + u * mag

class MetroNetwork(Network, metro.MetroSystem):
    def get_U(self):
        def U_node_field_func(node):
            if not 0.0 < node.r[0] < 1.0: return 100.0
            if not 0.0 < node.r[1] < 1.0: return 100.0
            return 0.0

        def U_node_inter_func(node):
            func = potentials.LJ(0.05, 1.0)
            U_node_inter = 0.0
            for i in range(len(self.nodes)):
                node_2 = self.nodes[i]
                if node is not node_2:
                    U_node_inter += func(utils.vector_mag_sq(node.r - node_2.r))
            return U_node_inter

        U = 0.0
        for i in range(len(self.nodes)):
            node = self.nodes[i]
            U += U_node_field_func(node)
#            U += U_node_inter_func(node)
        return U

    def store_state(self):
        self.node_rs_0 = [node.r.copy() for node in self.nodes]

    def revert_state(self):
        for i in range(len(self.nodes)):
            self.nodes[i].r = self.node_rs_0[i].copy()

    def perturb(self):
        i = np.random.randint(len(self.nodes))
        self.nodes[i].r += np.random.uniform(-0.01, 0.01, self.d)

def JSONHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))

def points_to_network(rs, labels):
    rs -= np.min(rs, axis=0)
    rs /= np.max(rs, axis=0)

    rs -= 0.5
    rs *= 0.9
    rs += 0.5

    nodes = []
    for i in range(len(rs)):
        nodes.append(Node(rs[i], labels[i]))
    return MetroNetwork(nodes)

def places_to_network(places):
    rs = np.zeros([len(places), 2], dtype=np.float)
    labels = []
    for i in range(len(places)):
        place = places[i]
        loc = place['geometry']['location']
        rs[i, :] = [loc['lat'], loc['lng']]
        labels.append(place['name'])
    network = points_to_network(rs, labels)
    network.simplify()
    return network

def main():
    rs = np.random.uniform(0.0, 1.0, size=(60, 2))
    labels = ['' for _ in range(len(rs))]
    network = points_to_network(rs, labels)
    for i in range(500):
        if not i % 20: network.plot(fname=i)
#        network.simplify()
        network.iterate(0.1)
        print(i, network.get_U())

if __name__ == '__main__':
    main()