from __future__ import print_function
import json
import itertools
import numpy as np
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
        self.edge_angle_U = 10.0
        ### Edge physical length
        self.edge_r_U = 10.0
        ### Edge fixed length
        self.edge_l_U = 1.0

        # Internode
        ## Length scale
        self.node_inter_r = 0.08
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
        self.U_changed = True
        self.inter_U_changed = np.ones(2 * [self.o], dtype=np.bool) - np.identity(self.o, dtype=np.bool)
        self.inter_U_cached = np.zeros(2 * [self.o], dtype=np.float)
         # Give each node an index to make cache access easier
        for i in range(self.o):
            self.ns[i].i = i

    def calc_pos_U(self, n):
        U = 0.0
        for x in n.r:
            if not 0.0 <= x <= 1.0:
                U += np.inf
        return U
    def pos_U(self, n):
        return self.calc_pos_U(n)

    def calc_inter_U(self, n, n2):
        if n is n2: return 0.0
        return self.node_inter_U_func(sep_mag_sq(n, n2))
    def inter_U(self, n, n2):
        if self.inter_U_changed[n.i, n2.i]:
            self.inter_U_cached[n.i, n2.i] = self.calc_inter_U(n, n2)
            self.inter_U_changed[n.i, n2.i] = False
        return self.inter_U_cached[n.i, n2.i]

    def calc_inters_U(self, n):
        U = 0.0
        for n2 in self.ns:
            U += self.inter_U(n, n2)
        return U
    def inters_U(self, n):
        return self.calc_inters_U(n)

    def calc_degree_U(self, n):
        deg = degree(n, self.ps)
        if deg == 0: return self.node_deg_U_0
        elif deg == 1: return self.node_deg_U_1
        elif deg == 2: return self.node_deg_U_2
        else: return self.node_deg_U_func(deg)
    def degree_U(self, n):
        return self.calc_degree_U(n)

    def calc_node_U(self, n):
        U = 0.0
        U_pos = self.pos_U(n)
        U_inter = self.inters_U(n)
        U_deg = self.degree_U(n) 
        U = U_pos + U_inter + U_deg
        return U
    def node_U(self, n):
        return self.calc_node_U(n)

    def calc_nodes_U(self):
        U = 0.0
        for n in self.ns:
            U += self.node_U(n)
        return U
    def nodes_U(self):
        return self.calc_nodes_U()

    def calc_edge_U(self, r):
        # Angle
        theta = np.arctan2(r[1], r[0])
        U_angle = self.edge_angle_U * (1.0 - np.cos(4.0 * theta) ** 2)
        # Physical length
        U_r = self.edge_r_U * np.sqrt(np.sum(np.square(r)))
        # Fixed length
        U_l = self.edge_l_U
        U = U_angle + U_r + U_l
        return U
    def edge_U(self, r):
        return self.calc_edge_U(r)

    def calc_path_U(self, p):
        U = 0.0
        for i in range(len(p.ns) - 1):
            U += self.edge_U(sep(p.ns[i], p.ns[i + 1]))
        return U
    def path_U(self, p):
        return self.calc_path_U(p)

    def calc_paths_U(self):
        U = 0.0
        for p in self.ps:
            U += self.path_U(p)
        return U
    def paths_U(self):
        return self.calc_paths_U()

    def calc_U(self):
        U = 0.0
        U_nodes = self.nodes_U()
        U_paths = self.paths_U()
        U = U_nodes + U_paths
        return U
    def U(self):
        if self.U_changed:
            self.U_cache = self.calc_U()
            self.U_changed = False
        return self.U_cache

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
        # Update cache
        self.cache_flag_update_swap()
    def revert_swap_edges(self):
        self.p_store.ns = self.ns_store[:]
        # Update cache
        self.cache_flag_update_swap()        
    def cache_flag_update_swap(self):
        # Total energy
        self.U_changed = True
        # TODO NEEDS TO WORK WITH CACHED EDGE ENERGIES

    def displace_node(self, i):
        # Get node to be jiggled
        n = self.ns[i]
        # Store current state
        self.n_store = n
        self.r_store = n.r.copy()
        # Displace
        n.r += np.random.uniform(-self.dr_max, self.dr_max, size=2)
        # Update cache
        self.cache_flag_update_node()
    def revert_displace_node(self):
        self.n_store.r = self.r_store.copy()
        # Update cache
        self.cache_flag_update_node()
    def cache_flag_update_node(self):
        # Total energy
        self.U_changed = True
        # Node energies
        self.inter_U_changed[self.n_store.i, :] = True
        self.inter_U_changed[:, self.n_store.i] = True
        # TODO NEEDS TO WORK WITH CACHED EDGE ENERGIES

    def iterate(self, beta):
        U_0 = self.U()

        i = np.random.randint(self.o + self.c)
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
        self.U_changed = True

class Node(object):
    def __init__(self, r, label=''):
        self.r = r
        self.label = label

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
        ns.append(Node(label=place['name'], r=np.array([loc['lat'], loc['lng']])))
    return ns

def random_nodes(n=50):
    ns = []
    for i in range(n):
        ns.append(Node(label='', r=np.random.uniform(-0.5, 0.5, size=2)))
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

    def __init__(self, ns, t=1000):
        self.t = t
        self.i = 0

        ps = initialise_paths(ns)
        self.mg = MetroGraph(ns, ps)

    def iterate(self):
        self.mg.iterate((self.i + 1.0) / self.t)
        self.i += 1

    def iterate_to_end(self):
        while self.i < self.t: self.iterate()

class MetroGraphPlotRunner(MetroGraphRunner):
    def __init__(self, ns, t=10000, every=100):
        MetroGraphRunner.__init__(self, ns, t)

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
                line = mpl.lines.Line2D(xs, ys, c=mpl.cm.autumn((float(p.label)/self.mg.ps[-1].label)*256.0))
                self.ax.add_line(line)
            self.ax.scatter(*get_rs(self.mg.ns).T)
            self.ax.set_xlim([-0.1, 1.1])
            self.ax.set_ylim([-0.1, 1.1])
            pp.draw()
            pp.cla()

        MetroGraphRunner.iterate(self)

def main():
    ns = random_nodes()
    mgr = MetroGraphRunner(ns)
    mgr.iterate_to_end()

if __name__ == '__main__':
    # main()
    import cProfile as cp
    cp.run('main()')
