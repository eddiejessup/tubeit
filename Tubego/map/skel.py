import json
import numpy as np
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as pp

#prop = fm.FontProperties(fname='London-Tube.ttf', size='small')

np.random.seed(116)

def dedupe(a):
    b = []
    for e in a: 
        if e not in b: b.append(e)
    return b

class Network(object):
    d = 2
    path_deets = (('Bakerloo', 'brown'),
                  ('Central', '#fe5806'),
                  ('Circle', 'yellow'),
                  ('District', '#00c131'),
                  ('East London', 'orange'),
                  ('Hammersmith and City', '#ff9cb6'),
                  ('Jubilee', '#8aa2af'),
                  ('Metropolitan', 'purple'),
                  ('Northern', '#4c554d'),
                  ('Piccadilly', 'blue'),
                  )

    def __init__(self, nodes, n_stops):
        self.nodes = nodes
        self.n_stops = n_stops
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

        i_path = 0
        while True:
            try:
                path = Path(*self.path_deets[i_path])
            except IndexError:
                path = Path('shink', 'black')

            while True:
                for node in make_node_list(path):
                    if node_valid(path, node):
                        path.extend(node)
                        break
                if len(path.nodes) > self.n_stops:# and self.is_terminus(path.end()):
                    break

            self.paths.append(path)
            if len(self.nodes_in_network()) == len(self.nodes):
                break
            i_path += 1

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

        pp.grid(True, color='#4ac6ff', linestyle='-')
        pp.xticks(np.arange(0.0, 1.01, 0.1))
        pp.yticks(np.arange(0.0, 1.01, 0.1))

        for node in self.nodes:
            if self.is_junction(node): 
                c = mpl.patches.Circle(node.r, radius=0.005, fc='white', ec='black', lw=2, zorder=10)
            else:
                ps = self.get_paths_node(node)
                if self.is_stop(node):
                    if len(ps) > 1:
                        c = mpl.patches.Circle(node.r, radius=0.0075, fc='black', lw=0, zorder=10)
                    else:
                        c = mpl.patches.Circle(node.r, radius=0.0075, fc=ps[0].color, lw=0, zorder=10)
                elif self.is_terminus(node):
                    assert len(ps) == 1
                    c = mpl.patches.Circle(node.r, radius=0.015, fc=ps[0].color, lw=0, zorder=10)
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
                l = mpl.lines.Line2D(r[:, 0], r[:, 1], color=p.color, lw=3)
                ax.add_line(l)

        if fname is None: pp.show()
        else: pp.savefig('%s.png' % fname)
        pp.cla()

    def jsonable(self):
        return [p.jsonable() for p in self.paths]

class Path(object):
    def __init__(self, label, color):
        self.label = label
        self.color = color
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
        self.node2.r = self.node1.r + np.array([np.cos(theta_s), np.sin(theta_s)]) * np.sqrt(np.sum(np.square(v)))

def JSONHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))

def make_points(n, r_sep_min):
    n_nodes = 200
    r_sep_min = 0.05

    rs = np.zeros([n, 2])
    for i in range(len(rs)):
        while True:
            rs[i] = np.random.uniform(0.0, 1.0, size=2)
            valid = True
            if not 0.0 < rs[i, 0] < 1.0: valid = False
            if not 0.0 < rs[i, 1] < 1.0: valid = False
            if i > 0 and np.sqrt(np.sum(np.square(rs[i] - rs[:i]), axis=-1)).min() < r_sep_min: valid = False
            if valid: break
    return rs

n_stops = 15

def main():
    rs = make_points(n_nodes, r_sep_min)
    network = points_to_network(rs)
    print('Dumping to JSON')
    d = json.dump(network, open('map.json', 'w'), default=ComplexHandler)
    print('Plotting')
    network.plot()
    print('Done')    

def points_to_network(rs):
    try:
        rs[0] - rs[1]
    except TypeError:
        rs = np.array(rs)
    print('Making nodes')
    nodes = [Node(r) for r in rs]
    print('Making network')
    network = Network(nodes, n_stops)
    print('Simplifying nodes')
#    for _ in range(50):
##        network.plot(fname=_)
#        network.simplify()
    return network

def normalise_points(points):
    pn = np.array(points)
    pn -= pn.min(axis=0)
    pn /= pn.max(axis=0)
    return pn

def places_to_points(places):
    points = []
    for place in places:
        loc = place['geometry']['location']
        points.append([loc['lat'], loc['lng']])
    return normalise_points(points)

def query_to_network(query, r):
    import place_search
    places = place_search.text_to_nearby(query)
    points = places_to_points(places)
    points = normalise_points(points)
    net = points_to_network(points)
    net.plot()

if __name__ == '__main__': 
#    main()
    query_to_network('whalley', 1000)