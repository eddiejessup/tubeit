import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pp
import networkx as nx

np.random.seed(116)

def jsonned(g):
    ns = []
    for n,d in g.nodes(data=True):
        ns.append({'label': d['label'], 'x': float(d['r'][0]), 'y': float(d['r'][1])})
    ps = []
    for p in paths(g):
        ps.append({'label': p.graph['label'], 'nodes': [int(n) for n in p.nodes()]})
    return json.dumps({'nodes': ns, 'paths': ps})

def paths(g):
    ps = {}
    for u,v,d in g.edges(data=True):
        path_label = d['path']
        if path_label not in ps.keys():
            ps[path_label] = nx.Graph([(u1,v1,d1) for u1,v1,d1 in g.edges(data=True) if d1['path'] is path_label], label=path_label)
    return ps.values()

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
    for p, c in zip(ps, np.linspace(0, 1, len(ps))):
        rs = []
        for u,v,d in p.edges(data=True):
            x, y = np.array([g.node[u]['r'], g.node[v]['r']]).T
            l = mpl.lines.Line2D(x, y, color=mpl.cm.jet(c), lw=3)
            ax.add_line(l)

    if fname is None: pp.show()
    else: fig.savefig('%s.png' % fname)

def sep(g, u, v):
    return g.node[v]['r'] - g.node[v]['r']

def sep_mag(g, u, v):
    return np.sqrt(np.sum(np.square(sep(g, u, v))))

def edge_energy(g, e):
    u, v = e
    sep = sep(g, u, v)
    theta = np.arctan2(sep[1], sep[0])
    U = np.cos(4 * theta) ** 2
    return U

def node_energy(g, n):
    U = 0.0
    for x in n['r']:
        if abs(x) > 0.5: U += 1.0
    return U

def graph_energy(g):
    U = 0.0
    for e in g.edges():
        U += edge_energy(g, e)
    for n in g.nodes():
        U += node_energy(g, n)
    return U

def orphans(g):
    return [n for n in g if not g.neighbors(n)]

def n_valid(g, p, n):
    if len(g.neighbors(n)) > 3: return False # Restrict number of neighbours
    if len(g.edges(n)) > 3: return False # Restrict number of edges
    # if len(g.neighbors(n)) == 1: return False # Leave termina as they are
    if n in p: return False # Stop paths passing through themselves
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
    p_length = 7

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

# def simplify(g):
#     r_sep_min = 0.03
#     thetas = np.linspace(-np.pi, np.pi, 9)

#     for p in paths(g):
#         for n1,n2,d in p.edges(data=True):
#             v = g.node[n2]['r'] - g.node[n1]['r']
#             theta_s = thetas[np.abs(thetas - np.arctan2(v[1], v[0])).argmin()]
#             u = np.array([np.cos(theta_s), np.sin(theta_s)])
#             mag = np.maximum(np.sqrt(np.sum(np.square(v))), r_sep_min)
#             r_new = g.node[n1]['r'] + u * mag
#             if np.all(np.abs(r_new) < 0.5): g.node[n2]['r'] = r_new

def simplify(g):
    sep_min = 0.15

    for u,v in g.edges():
        sep = sep(g, u, v)
        sep_mag = sep_mag(g, u, v)
        diff_mag = sep_min - sep_mag
        if diff_mag > 0.0:
            diff = (sep / sep_mag) * (diff_mag / 1.95)
            g.node[u]['r'] -= diff
            g.node[v]['r'] += diff

def places_graph(places):
    g = nx.MultiGraph()
    for i in range(len(places)):
        place = places[i]
        loc = place['geometry']['location']
        g.add_node(i, label=place['name'], r=np.array([loc['lat'], loc['lng']]))
    return g

def random_graph(g_nodes=100):
    g = nx.MultiGraph()
    for i in range(g_nodes):
        g.add_node(i, label='', r=np.random.uniform(-0.5, 0.5, size=2))
    return g

def main():
    g = random_graph()
    normalise_rs(g)
    grow(g)
    for _ in range(100): 
        simplify(g)
        print(graph_energy(g))
    # plot(g)
    # jdata = jsonned(g)
    # nx.draw(g)
    # pp.show()

if __name__ == '__main__':
    main()