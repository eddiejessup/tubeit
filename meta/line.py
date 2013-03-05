import matplotlib.pyplot as pp
import numpy as np
import utils

#def line_to_point(a, b, c, x, y):
#    return (a * x + b * y + c) / (a ** 2 + b ** 2) ** 0.5

#def line_to_point(m, c, x, y):
#    return (y - (m * x)) / (m ** 2 + 1) ** 0.5

def pick_inds(a, n=1):
    inds = []
    for i in range(n):
        while True:
            ind = np.random.randint(len(a))
            if ind not in inds:
                inds.append(ind)
                break
    return inds

#def make_line(r):
#    i_1 = np.random.randint(len(r))
#    while True:
#        i_2 = np.random.randint(len(r))
#        if i_1 != i_2: break
#    r_1 = r[i_1]
#    r_2 = r[i_2]
#    m = r_1[0] - r_2[0]
#    c = r_1[1] - m * r_1[0]
#    for i in range(len(r)):
#        print(line_to_point(m, c, r[i, 0], r[i, 1]))

def make_r(d, n=1, L=1.0, r_sep_min=0):
    r_sep_min_sq = r_sep_min ** 2
    rs = np.empty([n, d])
    for i in range(len(rs)):
        while True:
            r = np.random.uniform(-L / 2.0, L / 2.0, d)
            if i == 0 or utils.vector_mag_sq(rs[:i] - r).min() > r_sep_min_sq:
                rs[i] = r
                break
    return rs

# connectionality
c = 0.1
# vertices
n = 200
# path length
l = 10
# minimum vertex separation
r_sep_min = 0.03

# paths
p = int(round((c * n) / l))

def main():
    rs = make_r(2, n, 1.0, r_sep_min)
    np.random.shuffle(rs)
    for r in rs:
        pp.scatter(r[0], r[1])
    for i in range(p):
        inds = pick_inds(rs, l)
        r_sub = rs[inds]
        pp.plot(r_sub[:, 0], r_sub[:, 1])
    pp.axis('equal')
    pp.show()

if __name__ == '__main__':
    main()