from __future__ import print_function
import json
import itertools
import numpy as np
import scipy.spatial
import matplotlib as mpl
import matplotlib.pyplot as pp
import potentials

np.random.seed(116)

class MetroGraph(object):
    def __init__(self, nodes, paths, dr_max=0.02):
        self.ns = nodes
        self.ps = paths
        self.o = len(self.ns)
        self.c = len(self.ps)

        # Normalise rs
        rs = get_rs(self.ns)
        rs -= np.min(rs, axis=0)
        rs /= np.max(rs, axis=0)
        for n, r in zip(self.ns, rs):
            n.r = r

        # Perturbation
        self.dr_max = dr_max

        # Energy scales
        ### Internode
        self.node_inter_U = 0.4
        ### Node degree
        self.node_deg_U = 10.0
        ### Edge angle
        self.edge_angle_U = 1.0
        ### Edge physical length
        self.edge_r_U = 10.0
        ### Edge fixed length
        self.edge_l_U = 1.0

        # Internode
        ## Length scale
        self.node_inter_r = 0.1
        ## Function
        self.node_inter_U_func = potentials.LJ(self.node_inter_r, self.node_inter_U)

        # Degree
        ## Explicit energies
        self.node_deg_U_0 = 1.0
        self.node_deg_U_1 = 1.0
        self.node_deg_U_2 = 1.0
        ## Length scale
        self.node_deg_r = 2.0
        ## Function
        self.node_deg_U_func = potentials.LJ(self.node_deg_r, self.node_deg_U)

        # Cache
        self.inter_U_changed = True
        self.inter_U_cached = None

    def pos_U(self, n):
        U = 0.0
        for x in n.r:
            if not 0.0 <= x <= 1.0:
                U += np.inf
        return U

    def degree_U(self, n):
        deg = degree(n, self.ps)
        if deg == 0: return self.node_deg_U_0
        elif deg == 1: return self.node_deg_U_1
        elif deg == 2: return self.node_deg_U_2
        else: return self.node_deg_U_func(deg)

    def inters_U(self):
        if self.inter_U_changed:
            # print('changed')
            rdists = scipy.spatial.distance.pdist(get_rs(self.ns), metric='sqeuclidean')
            # print(self.node_inter_U_func(rdists).shape)
            self.inter_U_cached = 2.0 * np.sum(self.node_inter_U_func(rdists))
            self.inter_U_changed = False
        # else:
        #     print('noonononon')
        return self.inter_U_cached

    def nodes_U(self):
        U = 0.0
        for n in self.ns:
            U += self.pos_U(n)
            U += self.degree_U(n) 
        U += self.inters_U()
        return U

    def edge_U(self, r):
        # Angle
        theta = np.arctan2(r[1], r[0])
        U_angle = self.edge_angle_U * (1.0 - np.cos(4.0 * theta) ** 2)
        # Physical length
        # U_r = self.edge_r_U * np.sqrt(np.sum(np.square(r)))
        # Fixed length
        U_l = self.edge_l_U
        U = U_angle + U_l
        return U

    def paths_U(self):
        U = 0.0
        for p in self.ps:
            for i in range(len(p.ns) - 1):
                U += self.edge_U(sep(p.ns[i], p.ns[i + 1]))
        return U

    def U(self):
        U = 0.0
        U_nodes = self.nodes_U()
        U_paths = self.paths_U()
        U = U_nodes + U_paths
        return U

    def swap_edges(self, i):
        # Get list to be jiggled
        p = self.ps[i]
        # Store current state
        self.p_store = p
        self.ns_store = p.ns[:]
        # Swap
        # This might result in i_n2 == i_n2, not really a problem though
        i_n1 = np.random.randint(len(p.ns))
        i_n2 = np.random.randint(len(p.ns))
        p.ns[i_n1], p.ns[i_n2] = p.ns[i_n2], p.ns[i_n1]

    def revert_swap_edges(self):
        self.p_store.ns = self.ns_store[:]

    def displace_node(self, i):
        # Get node to be jiggled
        n = self.ns[i]
        # Store current state
        self.n_store = n
        self.r_store = n.r.copy()
        # Displace
        n.r += np.random.uniform(-self.dr_max, self.dr_max, size=2)
        # Update cache
        self.inter_U_changed= True
    def revert_displace_node(self):
        self.n_store.r = self.r_store.copy()
        # Update cache
        self.inter_U_changed= True

    def iterate(self, beta):
        U_0 = self.U()

        i = np.random.randint(self.o)
        if i < self.o:
            self.displace_node(i)
            revert = self.revert_displace_node
        elif self.o <= i < self.o + self.c:
            self.swap_edges(i - self.o)
            revert = self.revert_swap_edges
        else:
            raise Exception

        dU = self.U() - U_0
        if dU > 0.0 and np.exp(-beta * dU) < np.random.uniform():
            revert()

    def json(self):
        ns = []
        for n in self.ns:
            ns.append({'label': n.label, 'x': float(n.r[0]), 'y': float(n.r[1])})
        ps = []
        for p in self.ps:
            ps.append({'label': p.label, 'nodes': [n.i for n in p.ns]})
        return json.dumps({'nodes': ns, 'paths': ps})

class Path(object):
    def __init__(self, nodes, label=''):
        # Make sure the node list is mutable
        self.ns = list(nodes)
        self.label = label

class Node(object):
    def __init__(self, r, i, label=''):
        self.r = r
        self.label = label
        self.i = i

# Utils

def connecteds(ps):
    ns = []
    for p in ps: ns.extend(p.ns)
    return set(ns)

def isolateds(ns, ps):
    return set(ns).difference(connecteds(ps))

def get_rs(ns):
    return np.array([n.r for n in ns])

def sep(u, v):
    return u.r - v.r

def sep_mag_sq(u, v):
    return np.sum(np.square(sep(u, v)))

def sep_mag(u, v):
    return np.sqrt(sep_mag_sq(u, v))

def length(ns):
    rs = get_rs(ns)
    return np.sqrt(np.sum(np.square(rs[1:] - rs[:-1])))

def degree(n, ps):
    return sum((n in p.ns for p in ps))

# Initialisation

def places_nodes(places):
    ns = []
    for i in range(len(places)):
        place = places[i]
        loc = place['geometry']['location']
        ns.append(Node(label=place['name'], r=np.array([loc['lat'], loc['lng']]), i=i))
    return ns

def random_nodes(n=50):
    ns = []
    for i in range(n):
        ns.append(Node(label='', r=np.random.uniform(-0.5, 0.5, size=2), i=i))
    return ns

def initialise_paths(ns, ps_length=6, p_length=6):
    ps = []
    i = 0
    # Make sure to include every node
    while isolateds(ns, ps) or len(ps) < ps_length:
        # Get a random selection of isolated nodes, of max length p_length
        ns_base = list(np.random.permutation(list(isolateds(ns, ps)))[:p_length])
        # If there aren't enough isolated nodes, go for random ones
        if len(ns_base) < p_length:
            ns_base += list(np.random.permutation(ns)[:p_length - len(ns_base)])
        # Minimise path length travelling-salesman-wise
        ns_min = minimise_path(ns_base, length)

        ps.append(Path(nodes=ns_min, label=i))
        i += 1
    return ps

def minimise_path(ns_base, length_func):
    ns_base = tuple(ns_base)
    ns_min = ns_base
    l_min = length_func(ns_base)
    for ns in itertools.permutations(ns_base):
        l = length_func(ns)
        if l < l_min:
            ns_min = tuple(ns)
            l_min = l
    return ns_min

class MetroGraphRunner(object):

    def __init__(self, ns, t=100, b=100.0):
        self.t = t
        self.i = 0
        self.b = b

        ps = initialise_paths(ns)
        self.mg = MetroGraph(ns, ps)

    def iterate(self):
        self.mg.iterate(self.b * (self.i + 1.0) / self.t)
        self.i += 1

    def iterate_to_end(self):
        while self.i < self.t: self.iterate()

class MetroGraphPlotRunner(MetroGraphRunner):
    def __init__(self, ns, every=400, **kwargs):
        MetroGraphRunner.__init__(self, ns, **kwargs)
        self.every = every
        
        self.fig = pp.figure()
        self.ax = self.fig.gca()
        pp.ion()
        pp.show()

    def iterate(self):
        if not self.i % self.every:

            print(self.mg.U())

            for p in self.mg.ps:
                xs, ys = [], []
                for n in p.ns:
                    xs.append(n.r[0])
                    ys.append(n.r[1])
                line = mpl.lines.Line2D(xs, ys, c=mpl.cm.jet(float(p.label)/self.mg.ps[-1].label))
                self.ax.add_line(line)
            self.ax.scatter(*get_rs(self.mg.ns).T)
            self.ax.set_xlim([-0.1, 1.1])
            self.ax.set_ylim([-0.1, 1.1])
            pp.draw()
            pp.cla()

        MetroGraphRunner.iterate(self)

def main():
    ns = random_nodes()
    mgr = MetroGraphPlotRunner(ns)
    mgr.iterate_to_end()

if __name__ == '__main__':
    main()
