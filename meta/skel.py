import numpy as np
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as pp
import utils

prop = fm.FontProperties(fname='/home/ejm/London-Tube.ttf', size='small')

np.random.seed(113)

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

    def get_vert(self, node):
        for vert in self.verts:
            if vert.link(self) is node: return vert
        return False

    def get_sep(self, node):
        return utils.vector_mag(self.r - node.r)

    def get_lines(self):
        lines = []
        for vert in self.verts:
            for line in vert.lines:
                if line not in lines: lines.append(line)
        print(len(lines))
        return lines

    def is_alone(self):
        return len(self.verts) == 0
    
    def is_terminus(self):
        return len(self.verts) == 1
    
    def is_stop(self):
        return len(self.verts) == 2
    
    def is_junction(self):
        return len(self.verts) > 2

class Vertex(object):
    def __init__(self, node_1, node_2, line):
        node_1.verts.append(self)
        node_2.verts.append(self)
        self.nodes = (node_1, node_2)

        self.lines = [line]

    def add_line(self, line):
        self.lines.append(line)

    def link(self, node):
        if node is self.nodes[0]: return self.nodes[1]
        elif node is self.nodes[1]: return self.nodes[0]
        else: raise Exception

    def is_linked(self, node):
        return node in self.nodes

    def get_v(self):
        return self.nodes[1].r - self.nodes[0].r

    def get_u_perp(self):
        u = self.get_v()
        u /= np.sqrt(np.sum(np.square(u)))
        u_perp = u.copy()
        u_perp[0] = u[1]
        u_perp[1] = -u[0]
        return u_perp

    def get_offset(self, d):
        return d * self.get_u_perp()

    def get_r_1(self):
        return self.nodes[0].r

    def get_r_2(self):
        return self.nodes[1].r

    def get_x(self, d=0):
        return np.array([self.get_r_1()[0], self.get_r_2()[0]]) + self.get_offset(d)[0]

    def get_y(self, d=0):
        return np.array([self.get_r_1()[1], self.get_r_2()[1]]) + self.get_offset(d)[1]

    def __str__(self):
        return '( %6.2g, %6.2g ) --- ( %6.2g, %6.2g )' % (self.nodes[0].r[0], self.nodes[0].r[1], self.nodes[1].r[0], self.nodes[1].r[1])

    def simplify(self):
        thetas = np.linspace(-np.pi, np.pi, 9)
        v = self.get_v()
        theta = np.arctan2(v[1], v[0])
        theta_s = thetas[np.abs(thetas - theta).argmin()]
        u_s = np.array([np.cos(theta_s), np.sin(theta_s)])
        v_s = u_s * np.sqrt(np.sum(np.square(v)))
        self.nodes[1].r = self.get_r_1() + v_s

d = 2
n_nodes = 200
n_lines = 10
n_stops = 30
off_step = 0.004

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

r_sep_min = 0.02

rs = np.zeros([n_nodes, d])
for i in range(len(rs)):
    while True:
        rs[i, 0] = np.random.normal(loc=x_mid, scale=x_range)
        rs[i, 1] = np.random.normal(loc=y_mid, scale=y_range)
        valid = True
        if not x_min < rs[i, 0] < x_max: valid = False
        if not y_min < rs[i, 1] < y_max: valid = False
        if rs[i, 0] < 0.35 and rs[i, 1] < 0.12: valid = False
        if i > 0 and utils.vector_mag(rs[i] - rs[:i]).min() < r_sep_min: valid = False
        if valid: break

nodes = []
for i in range(len(rs)):
    nodes.append(Node(rs[i]))

verts = []

for line_key in line_deets:
    name, color = line_deets[line_key]
    line = Line(name, color)
    nodes_used = [np.random.permutation(nodes)[0]]
    for i_stop in range(n_stops):
        R = [nodes_used[-1].get_sep(node_2) for node_2 in nodes]
        for i_node in np.argsort(R):
            node_close = nodes[i_node]
            if node_close not in nodes_used:
                if node_close.is_neighb(nodes_used[-1]):
                    node_close.get_vert(nodes_used[-1]).add_line(line)
                else:
                    verts.append(Vertex(nodes_used[-1], node_close, line))
                nodes_used.append(node_close)
                break

fig = pp.figure()
ax = fig.gca()
ax.set_aspect('equal')
ax.set_xlim([-x_buff, x_max+x_buff])
ax.set_ylim([-y_buff, y_max+y_buff])

for _ in range(10):
    for vert in verts:
        vert.simplify()

for vert in verts:
    off = 0.0
#    vert.simplify()
    for line in vert.lines:
        r_x, r_y = vert.get_x(off), vert.get_y(off)
        l = mpl.lines.Line2D(r_x, r_y, color=line.color, lw=3)
        ax.add_line(l)
        off += off_step
#        v_s = vert.get_v_simple()
#        r_x[1] = r_x[0] + v_s[0]
#        r_y[1] = r_y[0] + v_s[1]
#        l = mpl.lines.Line2D(r_x, r_y, color=line.color, lw=3)
#        ax.add_line(l)

for node in nodes:
    if node.is_alone(): 
        continue
    elif node.is_junction():
        c = mpl.patches.Circle(node.r, radius=0.005, fc='white', ec='black', lw=2, zorder=10)
    elif node.is_stop():
#        c = mpl.patches.Circle(node.r, radius=0.003, fc=node.verts[0].lines[0].color, lw=0, zorder=10)
        c = mpl.patches.Circle(node.r, radius=0.003, fc='black', lw=0, zorder=10)
    elif node.is_terminus():
        line = node.verts[0].lines[0]
        c = mpl.patches.Circle(node.r, radius=0.007, fc=line.color, lw=0, zorder=10)
    ax.add_patch(c)

pp.grid(True, color='#4ac6ff', linestyle='-')
pp.xticks(np.arange(0.0, 0.901, 0.1))
pp.yticks(np.arange(0.0, 0.601, 0.1))

leg_lines = []
for key in line_deets:
    name, color = line_deets[key]
    leg_lines.append(mpl.lines.Line2D([0.0, 0.0], [0.0, 0.0], color=color, label=name))
pp.legend(leg_lines, loc='lower left', prop=prop)

pp.show()