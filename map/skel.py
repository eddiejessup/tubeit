import json
import itertools
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pp
import networkx as nx
import nx_utils as nxu

np.random.seed(116)

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
        else: # orphan
            c = mpl.patches.Circle(g.node[n]['r'], radius=0.015, fc='red', lw=0, zorder=10)
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

def get_rs(g):
    return np.array([g.node[n]['r'] for n in g])

def normalise_rs(g):
    rs = get_rs(g)

    rs -= np.min(rs, axis=0)
    rs /= np.max(rs, axis=0)

    for n, r in zip(g, rs):
        g.node[n]['r'] = r

def grow(g):
    p_length_mean = 6
    p_rlength_max = 1.0

    i_p = 0
    while nxu.orphans(g):
        p_length = np.random.randint(p_length_mean - 1, p_length_mean + 2)
        p_base = np.random.permutation(g.nodes())[:p_length]
        p_rlength_min = np.inf
        for p in itertools.permutations(p_base):
            p_rlength = np.sum([nxu.sep_mag(g, p[i], p[i + 1]) for i in range(p_length - 1)])
            if p_rlength < p_rlength_min: 
                p_rlength_min = p_rlength
                p_min = list(p)
        g.add_path(p_min, path=i_p, Uf=True)
        i_p += 1

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
    simplify(g)
    plot(g)

if __name__ == '__main__':
    main()