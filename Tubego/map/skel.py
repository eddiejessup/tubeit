import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pp
import networkx as nx

np.random.seed(116)

def jsonned(g):
    ns = g.nodes(data=True)
    ps = paths(g)
    ps = {k: ps[k].nodes() for k in ps}
    return {'nodes': ns, 'paths': ps}

def paths(g):
    ps = {}
    for u,v,d in g.edges(data=True):
        path_label = d['path']
        if path_label not in ps.keys():
            ps[path_label] = nx.Graph([(u1,v1,d1) for u1,v1,d1 in g.edges(data=True) if d1['path'] is path_label])
    return ps

def plot(g, fname=None):
    fig = pp.figure()
    ax = fig.gca()
    ax.set_aspect('equal')
    ax.set_xlim([-0.6, 0.6])
    ax.set_ylim([-0.6, 0.6])

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
    for p, c in zip(ps.values(), np.linspace(0, 1, len(ps))):
        rs = []
        for u,v,d in p.edges(data=True):
            x, y = np.array([g.node[u]['r'], g.node[v]['r']]).T
            l = mpl.lines.Line2D(x, y, color=mpl.cm.jet(c), lw=3)
            ax.add_line(l)

    if fname is None: pp.show()
    else: fig.savefig('%s.png' % fname)

def n_sep(g, n1, n2):
    return np.sqrt(np.sum(np.square(g.node[n1]['r'] - g.node[n2]['r'])))

def orphans(g):
    return [n for n in g if not g.neighbors(n)]

def n_valid(g, p, n):
    if len(g.neighbors(n)) > 3: return False # Restrict number of neighbours
    if len(g.edges(n)) > 3: return False # Restrict number of edges
    if len(g.neighbors(n)) == 1: return False # Leave termina as they are
    if n in p: return False # Stop paths passing through themselves
    if p and g.number_of_edges(p[-1], n) > 1: return False # Restrict number of parallel edges
    return True

def n_list(g, p):
    if not p:
        return np.random.permutation(orphans(g))
    else:
        inds = np.argsort([n_sep(g, p[-1], n) for n in g])
        return [g.nodes()[i] for i in inds]

def places_to_graph(places):
    g = nx.MultiGraph()
    for i in range(len(places)):
        place = places[i]
        loc = place['geometry']['location']
        g.add_node(place['name'], r=np.array([loc['lat'], loc['lng']]))

def normalise_rs(g):
    rs = np.array([g.node[n]['r'] for n in g])
    rs -= rs.mean()
    rs /= 2 * np.max(np.abs(rs), axis=0)
    for n, r in zip(g, rs):
        g.node[n]['r'] = r

def grow(g):
    p_length = 15

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
        g.add_path(p, path=i_p)
        i_p += 1

def simplify(g):
    r_sep_min = 0.07
    thetas = np.linspace(-np.pi, np.pi, 9)

    for e in g.edges():
        n1, n2 = e
        v = g.node[n2]['r'] - g.node[n1]['r']
        theta_s = thetas[np.abs(thetas - np.arctan2(v[1], v[0])).argmin()]
        u = np.array([np.cos(theta_s), np.sin(theta_s)])
        mag = np.maximum(np.sqrt(np.sum(np.square(v))), r_sep_min)
        r_new = g.node[n1]['r'] + u * mag
        if np.all(np.abs(r_new) < 0.5): g.node[n2]['r'] = r_new
    return g

def random_graph():
    g_nodes = 100

    g = nx.MultiGraph()
    rs = np.random.uniform(-0.5, 0.5, size=(g_nodes, 2))
    for i in range(len(rs)):
        g.add_node(i, r=rs[i])
    return g

def main():
    g = random_graph()
    normalise_rs(g)
    # print(orphans(g))
    grow(g)
    # for _ in range(100): simplify(g)
    # plot(g)
    print(jsonned(g))
    # nx.draw(g)
    # pp.show()

if __name__ == '__main__':
    main()