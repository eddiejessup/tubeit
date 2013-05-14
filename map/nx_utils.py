import numpy as np

def sep(g, u, v):
    return g.node[v]['r'] - g.node[u]['r']

def sep_mag(g, u, v):
    return np.sqrt(np.sum(np.square(sep(g, u, v))))

def orphans(g):
    return [n for n in g if not g.neighbors(n)]