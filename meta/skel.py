import numpy as np
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as pp

prop = fm.FontProperties(fname='London-Tube.ttf', size='small')

np.random.seed(115)

line_deets = {
    'baker': ('Bakerloo', 'brown'),
    'cent': ('Central', '#fe5806'),
    'circ': ('Circle', 'yellow'),
    'dist': ('District', '#00c131'),
    'elond': ('East London', 'orange'),
    'ham': ('Hammersmith & City', '#ff9cb6'),
    'jub': ('Jubilee', 'gray'),
    'metro': ('Metropolitan', 'purple'),
    'north': ('Northern', 'black'),
    'picc': ('Piccadilly', 'blue'),
}

def connect_nodes(vert):
    for node in vert.nodes:
        node.add_vert(vert)

class Line(object):
    def __init__(self, label, color):
        self.label = label
        self.color = color

class Node(object):
    def __init__(self, r):
        self.r = r
        self.verts = []

    def get_neighbs(self):
        return [vert.link(self) for vert in self.verts]

    def is_neighb(self, node):
        return node in self.get_neighbs()

    def add_vert(self, vert):
        # If node already knows about vertex, do nothing
        if vert in self.verts: return
        # If node already has a different vertex connecting to the same node, bad
        for vert_2 in self.verts:
            if vert.node_equiv(vert_2):
                raise Exception('Vertex connecting these nodes already exists')
        # Otherwise add the vertex
        self.verts.append(vert)

    def get_vert(self, node):
        for vert in self.verts:
            if vert.link(self) is node: return vert
        return False

    def get_sep(self, node):
        return np.sqrt(np.sum(np.square(self.r - node.r)))

    def n_verts(self):
        return len(self.verts)

    def get_lines(self):
        lines = []
        for vert in self.verts:
            for line in vert.lines:
                if line not in lines: lines.append(line)
        return lines

    def is_alone(self):
        return self.n_verts() == 0
    
    def is_terminus(self):
        return self.n_verts() == 1
    
    def is_stop(self):
        return self.n_verts() == 2
    
    def is_junction(self):
        return self.n_verts() > 2

    def simplify(self):
        thetas = np.linspace(-np.pi, np.pi, 9)
        for vert in self.verts:
            v = vert.get_v(self)
            theta = np.arctan2(v[1], v[0])
            theta_s = thetas[np.abs(thetas - theta).argmin()]
            u_s = np.array([np.cos(theta_s), np.sin(theta_s)])
            v_s = u_s * np.sqrt(np.sum(np.square(v)))
            vert.link(self).r = self.r + v_s

class Vertex(object):
    def __init__(self, node_1, node_2):
        self.nodes = (node_1, node_2)
        self.lines = []

    def n_lines(self):
        return len(self.lines)

    def add_line(self, line):
        self.lines.append(line)

    def node_equiv(self, vert_2):
        for node_2 in vert_2.nodes:
            if node_2 not in self.nodes: return False
        return True

    def link(self, node):
        if node is self.nodes[0]: return self.nodes[1]
        elif node is self.nodes[1]: return self.nodes[0]
        else: raise Exception

    def is_linked(self, node):
        return node in self.nodes

    def get_v(self, node):
        if node is self.nodes[0]: return self.nodes[1].r - self.nodes[0].r
        elif node is self.nodes[1]: return self.nodes[0].r - self.nodes[1].r
        else: raise Exception

    def get_u_perp(self, node):
        u = self.get_v(node)
        u /= np.sqrt(np.sum(np.square(u)))
        u_perp = u.copy()
        u_perp[0] = u[1]
        u_perp[1] = -u[0]
        return u_perp

    def get_offset(self, node, d):
        return d * self.get_u_perp(node)

    def get_r_1(self):
        return self.nodes[0].r

    def get_r_2(self):
        return self.nodes[1].r

    def get_r(self, node=None):
        if node is None: node = self.nodes[0]
        if node is self.nodes[0]: return np.array([self.get_r_1(), self.get_r_2()])
        elif node is self.nodes[1]: return np.array([self.get_r_2(), self.get_r_1()])
        else: raise Exception

    def get_r_offset(self, node, d):
        return self.get_r(node) + self.get_offset(node, d)

    def get_x(self, node=None):
        return self.get_r(node)[:, 0]

    def get_y(self, node=None):
        return self.get_r(node)[:, 1]

    def __str__(self):
        return '( %6.2g, %6.2g ) --- ( %6.2g, %6.2g )' % (self.nodes[0].r[0], self.nodes[0].r[1], self.nodes[1].r[0], self.nodes[1].r[1])

def make_points():
    rs = np.zeros([n_nodes, d])
    for i in range(len(rs)):
        while True:
            rs[i, 0] = np.random.normal(loc=x_mid, scale=x_range)
            rs[i, 1] = np.random.normal(loc=y_mid, scale=y_range)
            valid = True
            if not x_min < rs[i, 0] < x_max: valid = False
            if not y_min < rs[i, 1] < y_max: valid = False
            if rs[i, 0] < 0.35 and rs[i, 1] < 0.12: valid = False
            if i > 0 and np.sqrt(np.sum(np.square(rs[i] - rs[:i]), axis=-1)).min() < r_sep_min: valid = False
            if valid: break
    return rs

def make_nodes(rs):
    nodes = []
    for i in range(len(rs)):
        nodes.append(Node(rs[i]))
    return nodes

def make_lines(nodes):
    for line_key in line_deets:
        name, color = line_deets[line_key]
        line = Line(name, color)
        nodes_used = [np.random.permutation(nodes)[0]]
        for i_stop in range(n_stops):
            R = [nodes_used[-1].get_sep(node_2) for node_2 in nodes]
            for i_node in np.argsort(R):
                node_close = nodes[i_node]
                valid = True
                if node_close in nodes_used: valid = False
                if node_close.is_neighb(nodes_used[-1]):
                    vert = node_close.get_vert(nodes_used[-1])
                else:
                    vert = Vertex(nodes_used[-1], node_close)
                # Don't allow more than shared_vert_max lines on a vertex
                if vert.n_lines() >= shared_vert_max: valid = False
                if valid:
                    vert.add_line(line)
                    connect_nodes(vert)
                    nodes_used.append(node_close)
                    break

def simplify(nodes, n=1):
    for _ in range(n):
        for node in nodes:
            node.simplify()

def plot(nodes, fname='out'):
    fig = pp.figure()
    ax = fig.gca()
    ax.set_aspect('equal')
    ax.set_xlim([-x_buff, x_max+x_buff])
    ax.set_ylim([-y_buff, y_max+y_buff])

    pp.grid(True, color='#4ac6ff', linestyle='-')
    pp.xticks(np.arange(0.0, 0.901, 0.1))
    pp.yticks(np.arange(0.0, 0.601, 0.1))

    leg_lines = []
    for key in line_deets:
        name, color = line_deets[key]
        leg_lines.append(mpl.lines.Line2D([0.0, 0.0], [0.0, 0.0], color=color, label=name))
    pp.legend(leg_lines, loc='lower left', prop=prop)

    verts_plot = []
    for node in nodes:

        if node.is_alone(): 
            continue
        elif node.is_junction():
            c = mpl.patches.Circle(node.r, radius=0.005, fc='white', ec='black', lw=2, zorder=10)
        elif node.is_stop():
            c = mpl.patches.Circle(node.r, radius=0.003, fc='black', lw=0, zorder=10)
        elif node.is_terminus():
            line = node.verts[0].lines[0]
            c = mpl.patches.Circle(node.r, radius=0.007, fc=line.color, lw=0, zorder=10)
        ax.add_patch(c)

        for vert in node.verts:
            if vert not in verts_plot:
                if vert.n_lines() % 2: off_mag = off_step / 2.0
                else: off_mag = 0.0
                off_sign = 1
                for line in vert.lines:
                    r = vert.get_r_offset(node, off_mag * off_sign)
                    r_x, r_y = r[:, 0], r[:, 1]
                    style = mpl.patches.ArrowStyle.Curve()
                    l = mpl.patches.FancyArrowPatch(r[0], r[1], color=line.color, arrowstyle='fancy', connectionstyle='arc3', lw=3.0/vert.n_lines(), aa=True)
                    ax.add_patch(l)
#                    l = mpl.lines.Line2D(r_x, r_y, color=line.color, lw=3.0/vert.n_lines())
#                    ax.add_line(l)
                    if off_sign == -1: off_mag += off_step
                    off_sign *= -1
                verts_plot.append(vert)

    pp.show()
#    pp.savefig('%s.png' % fname)
    ax.cla()
    
# Point generation
r_sep_min = 0.04
x_min = 0.0
y_min = 0.0
x_max = 0.9
y_max = 0.6
x_mid = (x_min + x_max) / 2.0
y_mid = (y_min + y_max) / 2.0
x_range = x_max - x_min
y_range = y_max - y_min
x_buff = x_range / 20.0
y_buff = y_range / 20.0

# Map generation
d = 2
n_nodes = 100
n_lines = 10
n_stops = 30
shared_vert_max = 4
n_simplify = 3

# Presentation
off_step = 0.003

rs = make_points()
nodes = make_nodes(rs)
make_lines(nodes)
simplify(nodes, n_simplify)
plot(nodes)