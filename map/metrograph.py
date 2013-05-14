import numpy as np
import potentials
import nx_utils as nxu

class MetroGraph(object):
    def __init__(self, g):
        self.g = g
        self.internode_U = potentials.LJ(0.03, 1.0)

    def get_U(self):
        def edge_energy(u, v, d):
            if d['Uf']:
                r_sep = nxu.sep(self.g, u, v)
                theta = np.arctan2(r_sep[1], r_sep[0])
                U = 1.0 - np.cos(4.0 * theta) ** 2
                d['U'] = U
                d['Uf'] = False
            return d['U']

        def node_energy(n, d):
            if d['Uf']:
                U = 0.0

                for x in d['r']:
                    if not 0.0 <= x <= 1.0: 
                        U += np.inf

                if U < np.inf:
                    for n2 in self.g.nodes():
                        if n2 is not n:
                            U += self.internode_U(nxu.sep_mag(self.g, n, n2) ** 2)

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
        self.g.node[self.n_pert]['Uf'] = True

    def perturb(self, dr_max):
        self.g.node[self.n_pert]['r'] += np.random.uniform(-dr_max, dr_max, size=2)
        self.g.node[self.n_pert]['Uf'] = True
        for u,v,d in self.g.edges(self.n_pert, data=True):
            d['Uf'] = True

    def iterate(self, beta, dr_max):
        self.n_pert = self.g.nodes()[np.random.randint(len(self.g.nodes()))]
        U_0 = self.get_U()
        self.store_state()
        # print('orig: ', self.g.node[self.n_pert]['r'][0], self.get_U())
        self.perturb(dr_max)
        U_new = self.get_U()
        # print('perturbed: ', self.g.node[self.n_pert]['r'][0], self.get_U())
        if np.minimum(1.0, np.exp(-beta * (U_0 - U_new))) > np.random.uniform():
            self.revert_state()
            # print('reverted: ', self.g.node[self.n_pert]['r'][0], self.get_U())
        # else: 
            # print('kept: ', self.g.node[self.n_pert]['r'][0], self.get_U())
        # if U_0 == np.inf: 
        #     raise Exception

def simplify(g, beta=1.0, dr_max=0.01, i=10000):
    mg = MetroGraph(g)
    for _ in range(i): mg.iterate(beta, dr_max)