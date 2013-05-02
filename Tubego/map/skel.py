import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pp
import networkx as nx
import potentials

np.random.seed(116)

class MetroGraph(object):
    def __init__(self, g):
        self.g = g
        self.edge_length_U = potentials.LJ(0.03, 1.0)

    def get_U(self):
        def edge_energy(u, v, d):
            if d['Uf']:
                r_sep = sep(self.g, u, v)
                theta = np.arctan2(r_sep[1], r_sep[0])
                U = 1.0 - np.cos(4.0 * theta) ** 2
                U *= self.edge_length_U(sep_mag(self.g, u, v) ** 2)
                d['U'] = U
                d['Uf'] = False
            return d['U']

        def node_energy(n, d):
            if d['Uf']:
                U = 0.0
                for x in d['r']:
                    if not 0.0 < abs(x) < 1.0: U += 10.0
                d['U'] = U
                d['Uf'] = False
            return d['U']

        U = 0.0
        for n,d in self.g.nodes(data=True):
            U += node_energy(n, d)
        for u,v,d in self.g.edges(data=True):
            U += edge_energy(u, v, d)
        return U

    def store_state(self):
        self.r_old = self.g.node[self.n_pert]['r'].copy()

    def revert_state(self):
        self.g.node[self.n_pert]['r'] = self.r_old.copy()

    def perturb(self):
        self.g.node[self.n_pert]['r'] += np.random.uniform(-0.01, 0.01, size=2)
        self.g.node[self.n_pert]['Uf'] = True
        for u,v,d in self.g.edges(self.n_pert, data=True):
            d['Uf'] = True

    def iterate(self, beta):
        self.n_pert = self.g.nodes()[np.random.randint(len(self.g.nodes()))]
        U_0 = self.get_U()
        self.store_state()
        self.perturb()
        if np.minimum(1.0, np.exp(-beta * (U_0 - self.get_U()))) > np.random.uniform():
            self.revert_state()

def jsonned(g):
    ns = []
    for n,d in g.nodes(data=True):
        ns.append({'label': d['label'], 'x': float(d['r'][0]), 'y': float(d['r'][1])})
    ps = []
    for p in paths(g):
        ps.append({'label': p.graph['label'], 'nodes': [int(n) for n in p.nodes()]})
    return json.dumps({'nodes': ns, 'paths': ps})

def plot(g, fname=None):
    fig = pp.figure()
    ax = fig.gca()
    ax.set_aspect('equal')
    ax.set_xlim([-0.1, 1.1])
    ax.set_ylim([-0.1, 1.1])
    ax.set_xticks([])
    ax.set_yticks([])

    for n in g:
        if len(g.neighbors(n)) > 2: # junction
            c = mpl.patches.Circle(g.node[n]['r'], radius=0.005, fc='white', ec='black', lw=2, zorder=10)
        elif len(g.neighbors(n)) == 2: # stop
            c = mpl.patches.Circle(g.node[n]['r'], radius=0.0075, fc='blue', lw=0, zorder=10)
        elif len(g.neighbors(n)) == 1: # terminus
            c = mpl.patches.Circle(g.node[n]['r'], radius=0.015, fc='green', lw=0, zorder=10)
        else:
            raise Exception
        ax.add_patch(c)

    ps = paths(g)
    for p, c in zip(ps, np.linspace(0, 1, len(ps))):
        rs = []
        for u,v,d in p.edges(data=True):
            x, y = np.array([g.node[u]['r'], g.node[v]['r']]).T
            l = mpl.lines.Line2D(x, y, color=mpl.cm.jet(c), lw=3)
            ax.add_line(l)

    if fname is None: pp.show()
    else: fig.savefig('%s.png' % fname)

def paths(g):
    ps = {}
    for u,v,d in g.edges(data=True):
        path_label = d['path']
        if path_label not in ps.keys():
            ps[path_label] = nx.Graph([(u1,v1,d1) for u1,v1,d1 in g.edges(data=True) if d1['path'] is path_label], label=path_label)
    return ps.values()

def sep(g, u, v):
    return g.node[v]['r'] - g.node[u]['r']

def sep_mag(g, u, v):
    return np.sqrt(np.sum(np.square(sep(g, u, v))))

def orphans(g):
    return [n for n in g if not g.neighbors(n)]

def n_valid(g, p, n):
    if n in p: return False # Stop paths passing through themselves
    if len(g.neighbors(n)) > 2: return False # Restrict number of neighbours
    if len(g.edges(n)) > 3: return False # Restrict number of edges
    if p and g.number_of_edges(p[-1], n) > 2: return False # Restrict number of parallel edges
    return True

def n_list(g, p):
    if not p:
        return np.random.permutation(orphans(g))
    else:
        inds = np.argsort([sep_mag(g, p[-1], n) for n in g])
        return [g.nodes()[i] for i in inds]

def normalise_rs(g):
    rs = np.array([g.node[n]['r'] for n in g])
    rs -= np.min(rs, axis=0)
    rs /= np.max(rs, axis=0)
    rs -= 0.5
    rs *= 0.8
    rs += 0.5
    for n, r in zip(g, rs):
        g.node[n]['r'] = r

def grow(g):
    p_length = 10

    i_p = 0
    while orphans(g):
        p = []
        i_since_change = 0
        while i_since_change < 1000:
            for n in n_list(g, p):
                if n_valid(g, p, n):
                    p.append(n)
                    i_since_change = 0
                    break
            if len(p) > p_length:
                break
            i_since_change += 1
        g.add_path(p, path=i_p, Uf=True)
        i_p += 1

def simplify(g, i=10000):
    mg = MetroGraph(g)
    for _ in range(i): mg.iterate(0.3)

def places_graph(places):
    g = nx.MultiGraph()
    for i in range(len(places)):
        place = places[i]
        loc = place['geometry']['location']
        g.add_node(i, label=place['name'], r=np.array([loc['lat'], loc['lng']]), Uf=True)
    return g

def random_graph(g_nodes=100):
    g = nx.MultiGraph()
    for i in range(g_nodes):
        g.add_node(i, label='', r=np.random.uniform(-0.5, 0.5, size=2), Uf=True)
    return g

def main():
    g = random_graph()
    normalise_rs(g)
    grow(g)
    mg = MetroGraph(g)

    for _ in range(10000): 
        if not _ % 2000: 
            plot(mg.g, _)
            print(_)
        mg.iterate(0.3)
    # nx.draw(g)
    # pp.show()

if __name__ == '__main__':
    main()