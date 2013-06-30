from __future__ import print_function
import json
import itertools
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pp
import potentials

np.random.seed(116)

class MetroGraph(object):
    def __init__(self, nodes, paths, dr_max=0.01):
        self.ns = nodes
        self.ps = paths
        self.o = len(self.ns)

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
        self.node_inter_U = 0.1
        ### Node degree
        self.node_deg_U = 1.0
        ### Edge angle
        self.edge_angle_U = 1.0
        ### Edge physical length
        self.edge_r_U = 1.0
        ### Edge fixed length
        self.edge_l_U = 1.0

        # Internode
        ## Length scale
        self.node_inter_r = 0.06
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

    # def add_edge(self):
    #     while True:
    #         self.u = self.g.nodes()[np.random.randint(self.g.order())]
    #         self.v = self.g.nodes()[np.random.randint(self.g.order())]
    #         if not (self.u is self.v) and not self.v in self.g.edge[self.u]: break
    #     self.g.add_edge(self.u, self.v, Uf=True)

    # def revert_add_edge(self):
    #     self.g.remove_edge(self.u, self.v)

    # def remove_edge(self):
    #     self.u, self.v, self.d = self.g.edges(data=True)[np.random.randint(self.g.size())]
    #     self.g.remove_edge(self.u, self.v)

    # def revert_remove_edge(self):
    #     self.g.add_edge(self.u, self.v, **self.d)
    #     self.d['Uf'] = True

    def displace_node(self):
        # Pick node to displace
        i_node = np.random.randint(self.o)

        # Store current state
        self.u = self.ns[i_node]
        self.r = self.u.r.copy()

        # Displace
        self.u.r += np.random.uniform(-self.dr_max, self.dr_max, size=2)

    def revert_displace_node(self):
        self.u.r = self.r.copy()

    def cache_flag_update_node(self):
        # Graph energy
        self.U_changed = True
        # Node energy
        # self.inter_U_changed[...] = True
        self.inter_U_changed[self.u.i, :] = True
        self.inter_U_changed[:, self.u.i] = True
        # Node neighbouring edges
        # ! TODO NEEDS WORK TO WORK WITH PATHS
        # for u, v, d in self.g.edges(self.u, data=True):
        #     d['U_changed'] = True

    def iterate(self, beta):
        U_0 = self.U()

        i = np.random.randint(self.o)
        if i < self.o:
            self.displace_node()
            cache_flag_update = self.cache_flag_update_node
            revert = self.revert_displace_node
        # elif i == self.g.order():
        #     self.add_edge()
        #     revert = self.revert_add_edge
        # elif i == self.g.order() + 1:
        #     if self.g.size() == 0: return
        #     self.remove_edge()
        #     revert = self.revert_remove_edge
        else:
            raise Exception

        cache_flag_update()
        U_new = self.U()
        if np.exp(-beta * (U_new - U_0)) < np.random.uniform():
            revert()
            cache_flag_update()

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
        self.ns = nodes
        self.label = label
        self.U_changed = True

class Node(object):
    def __init__(self, r, label=''):
        self.r = r
        self.label = label

# def plot(g, fname=None):
#     fig = pp.figure()
#     ax = fig.gca()
#     ax.set_aspect('equal')
#     ax.set_xlim([-0.1, 1.1])
#     ax.set_ylim([-0.1, 1.1])
#     ax.set_xticks([])
#     ax.set_yticks([])

#     for n in g:
#         if len(g.neighbors(n)) > 2: # junction
#             c = mpl.patches.Circle(g.node[n]['r'], radius=0.005, fc='white', ec='black', lw=2, zorder=10)
#         elif len(g.neighbors(n)) == 2: # stop
#             c = mpl.patches.Circle(g.node[n]['r'], radius=0.0075, fc='blue', lw=0, zorder=10)
#         elif len(g.neighbors(n)) == 1: # terminus
#             c = mpl.patches.Circle(g.node[n]['r'], radius=0.015, fc='green', lw=0, zorder=10)
#         else: # orphan
#             c = mpl.patches.Circle(g.node[n]['r'], radius=0.015, fc='red', lw=0, zorder=10)
#         ax.add_patch(c)

#     for u,v,d in g.edges(data=True):
#         x, y = np.array([g.node[u]['r'], g.node[v]['r']]).T
#         l = mpl.lines.Line2D(x, y, color=mpl.cm.jet(c), lw=3)
#         ax.add_line(l)

#     if fname is None: pp.show()
#     else: fig.savefig('%s.png' % fname)


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

def initialise_paths(ns, p_length=5):
    ps = []
    i = 0
    while isolateds(ns, ps):
        ns_base = np.random.permutation(list(isolateds(ns, ps)))[:p_length]
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

def nodes_to_graph(ns, t=10000):
    ps = initialise_paths(ns)
    mg = MetroGraph(ns, ps)
    for i in range(t):
        mg.iterate(float(i) / t)
    return mg

def main():
    nodes = random_nodes()
    paths = initialise_paths(nodes)
    mg = MetroGraph(nodes, paths)

    fig = pp.figure()
    ax = fig.gca()
    pp.ion()
    pp.show()

    for i in range(100000):
        beta = i/100.0
        mg.iterate(beta)
        if not i % 100:
            print(mg.U())
            for p in mg.ps:
                xs, ys = [], []
                for n in p.ns:
                    xs.append(n.r[0])
                    ys.append(n.r[1])
                line = mpl.lines.Line2D(xs, ys, c=mpl.cm.autumn((float(p.label)/mg.ps[-1].label)*256.0))
                ax.add_line(line)
            ax.scatter(*get_rs(mg.ns).T)
            ax.set_xlim([-0.1, 1.1])
            ax.set_ylim([-0.1, 1.1])
            pp.draw()
            pp.cla()

if __name__ == '__main__':
    main()