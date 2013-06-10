import json
import itertools
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pp
import networkx as nx
import potentials

np.random.seed(116)

class MetroGraph(object):
    def __init__(self, g, paths):
        self.g = g
        self.path = paths

        # Cache
        self.U_changed = True
        self.inter_U_changed = np.ones(2 * [self.g.order()], dtype=np.bool) - np.identity(self.g.order(), dtype=np.bool)
        self.inter_U_cached = np.zeros(2 * [self.g.order()], dtype=np.float)

        self.dr_max = 0.015
        self.inter_U_func = potentials.LJ(0.06, 1.0)

    def calc_pos_U(self, n, d):
        U = 0.0
        for x in d['r']:
            if not 0.0 <= x <= 1.0:
                U += np.inf
        return U

    def pos_U(self, n, d):
        return self.calc_pos_U(n, d)

    def calc_inter_U_single(self, n, n2):
        if n is n2: return 0.0
        return self.inter_U_func(sep_mag_sq(self.g, n, n2))

    def inter_U_single(self, n, n2):
        if self.inter_U_changed[n, n2]:
            self.inter_U_cached[n, n2] = self.calc_inter_U_single(n, n2)
            self.inter_U_changed[n, n2] = False
        return self.inter_U_cached[n, n2]

    def calc_inter_U(self, n, d):
        U = 0.0
        for n2 in self.g:
            U += self.inter_U_single(n, n2)
        return U

    def inter_U(self, n, d):
        return self.calc_inter_U(n, d)

    def calc_node_U_single(self, n, d):
        U = 0.0
        U += self.pos_U(n, d)
        U += self.inter_U(n, d)
        return U

    def node_U_single(self, n, d):
        return self.calc_node_U_single(n, d)

    def node_U(self):
        U = 0.0
        for n, d in self.g.nodes(data=True):
            U += self.node_U_single(n, d)
        return U

    def path_U_single(self, p):
        for e in self.g.edges_iter(p.nodes):
            


    def path_U(self, p):
        U = 0.0
        g.remove_edges_from(self.g.edges())
        for p in self.paths:
            U += self.path_U_single(p)

    def calc_U(self):
        U = 0.0
        U += self.node_U()
        U += self.path_U()
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
        i_node = np.random.randint(self.g.order())

        # Store current state
        self.u, d = self.g.nodes(data=True)[i_node]
        self.r = d['r'].copy()

        # Displace
        d['r'] += np.random.uniform(-self.dr_max, self.dr_max, size=2)

    def revert_displace_node(self):
        self.g.node[self.u]['r'] = self.r.copy()

    def cache_flag_update_node(self):
        # Graph energy
        self.U_changed = True
        # Node energy
        # self.inter_U_changed[...] = True
        self.inter_U_changed[self.u, :] = True
        self.inter_U_changed[:, self.u] = True
        # Node neighbouring edges
        for u, v, d in self.g.edges(self.u, data=True):
            d['U_changed'] = True

    def iterate(self, beta):
        U_0 = self.U()

        i = np.random.randint(self.g.order())
        if i < self.g.order():
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

# def edge_length_U(u, v):
#     return sep_mag(u, v) * self.edge_U_density

# def edge_orient_U(u, v):
#     r = sep(u, v)
#     theta = np.arctan2(r[1], r[0])
#     return 1.0 - np.cos(4.0 * theta) ** 2

# def edge_U(u, v, d):
#     if d['Uf']:
#         U = 0.0
#         U += edge_orient_U(sep(u, v))
#         U += edge_length_U(sep_mag(u, v))
#         d['U'] = U
#         d['Uf'] = False
#     return d['U']

# class MetroSpaceGraph(object):
#     def __init__(self, nodes):
#         self.g = nx.MultiGraph(self.ns)
#         self.ps = {}

#         self.dr_max = 0.01
#         
#         self.edge_U_density = 1.0


#     def U(self):

#         def degree_U(self, d):
#             U = 0.0
#             for n, deg in self.g.degree_iter():
#                 if deg == 0: U += 10.0
#                 elif 1 <= deg <= 2: U += 2.0
#                 elif 3 <= deg <= 4: U += 2.0
#                 elif 5 <= deg <= 6: U += 1.0
#                 else: return np.inf
#         d = self.g.node[n]
#         if d['Uf']:
#             U = 0.0
#             U += pos_U(n.r)
#             U += degree_U(self.g.degree()[n])
#             U += inter_U(n)
#             d['U'] = U
#             d['Uf'] = False
#         return d['U']

#     return sum(U(n) for n in self.g)

#         U = 0.0
#         U += node_pos
#         U += node_degree
#         U += node_inter
#         U += edge_length
#         U += edge_orient
#         U += path_size

#         return nodes_U + 
#         edges_U = 0.0
#         for u,v,d in self.g.edges(data=True):
#             edges_U += edge_energy(u, v, d)
#         U = nodes_U + edges_U
#         return U

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

class Path(object):
    def __init__(self, nodes, label):
        self.nodes = nodes
        self.label = label
        self.U_changed = U_changed

def make_initial_paths(g):
    p_length_mean = 6
    p_rlength_max = 1.0

    i_p = 0
    paths = []
    while orphans(g):
        p_length = np.random.randint(p_length_mean - 1, p_length_mean + 2)
        p_base = np.random.permutation(g.nodes())[:p_length]
        p_min = p_base[:]
        # p_rlength_min = np.inf
        # for p in itertools.permutations(p_base):
        #     p_rlength = np.sum([sep_mag(g, p[i], p[i + 1]) for i in range(p_length - 1)])
        #     if p_rlength < p_rlength_min: 
        #         p_rlength_min = p_rlength
        #         p_min = list(p)
        paths.append(Path(nodes=Path(p_min), label=i_p))
        i_p += 1
    return paths

def sep(g, u, v):
    return g.node[v]['r'] - g.node[u]['r']

def sep_mag_sq(g, u, v):
    return np.sum(np.square(sep(g, u, v)))

def sep_mag(g, u, v):
    return np.sqrt(sep_mag_sq(g, u, v))

def orphans(g):
    return [n for n in g if not g.neighbors(n)]

def get_rs(g):
    return np.array([d['r'] for n,d in g.nodes(data=True)])

def normalise_rs(g):
    rs = get_rs(g)

    rs -= np.min(rs, axis=0)
    rs /= np.max(rs, axis=0)

    for n, r in zip(g, rs):
        g.node[n]['r'] = r

def places_graph(places):
    labels, rs = [], []
    for i in range(len(places)):
        place = places[i]
        loc = place['geometry']['location']
        labels.append(place['name'])
        rs.append(np.array([loc['lat'], loc['lng']]))
    return make_graph(labels, rs)

def random_graph(order=50):
    labels, rs = [], []
    for i in range(order):
        labels.append('')
        rs.append(np.random.uniform(-0.5, 0.5, size=2))
    return make_graph(labels, rs)

def make_graph(labels, rs):
    g = nx.MultiGraph()
    for i, label, r in zip(range(len(labels)), labels, rs):
        g.add_node(i, label=label, r=r)
    return g

def main():
    g = random_graph()
    normalise_rs(g)
    paths = make_initial_paths(g)
    mg = MetroGraph(g, paths)

    fig = pp.figure()
    ax = fig.gca()
    scat = ax.scatter(*get_rs(mg.g).T)
    ax.set_xlim([-0.1, 1.1])
    ax.set_ylim([-0.1, 1.1])
    pp.ion()
    pp.show()

    for i in range(10000):
        mg.iterate(1.0)
        if not i % 50:
            print(mg.U())
            scat.set_offsets(get_rs(mg.g))
            pp.draw()

if __name__ == '__main__':
    main()