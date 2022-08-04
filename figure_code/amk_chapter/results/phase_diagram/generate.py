#!/usr/bin/env python3
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1" 
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
rng = np.random.default_rng(43245426246)

import os

from koala import hamiltonian
from koala import example_graphs as eg
from koala.flux_finder import pathfinding

import pickle
from tqdm import tqdm
import itertools as it

from koala import hamiltonian


def line(start, end, npoints):
    t = np.linspace(0,1,npoints)[:, None]
    return start * (1-t) + end * t

symmetry_points = np.array([[0,0.5,0.5], [0.5,0,0.5], [0.5,0.5,0]])
center = np.array([1,1,1])/3
lines = []

triplets = np.array([
    [
    [0,0,1], #z
    [0, 0.5, 0.5],
    [0.5, 0, 0.5]
    ],
    [
    [0,1,0], #y
    [0.5, 0.5, 0],
    [0, 0.5, 0.5]
    ],
    [
    [1,0,0], #x
    [0.5, 0, 0.5],
    [0.5, 0.5, 0]
    ]
])

## User Parameters ### 
n_lines = 4
highlighted_line = 3
ts = np.linspace(0.5,1,50)
lattice, coloring, ujk, points = eg.make_amorphous(L = 15, return_points = True)

_, T_x = pathfinding.dual_loop(lattice, direction = 'x')
_, T_y = pathfinding.dual_loop(lattice, direction = 'y')


## End of user parameters

t = np.linspace(0,1,n_lines)[:, None]

logo_lines = []
for corner, left, right in triplets:
    line_ends = left * t + (1-t) * center
    line_ends2 = center * t + right * (1-t)
    line_ends = np.concatenate([line_ends2[:-1], line_ends])

    for e in line_ends:
        logo_lines.append([corner, e])
        
lines = np.array(logo_lines)

def gap_size_along_line(start_J, end_J, lattice, coloring, ujk): 
    def f(t):
        J = start_J * (1-t) + t * end_J
        maj_ham = hamiltonian.generate_majorana_hamiltonian(lattice, coloring, ujk, J)
        maj_energies = np.linalg.eigvalsh(maj_ham)
        return min(np.abs(maj_energies))
    return f
    
    
gap_vs_t = dict()

for x, y in tqdm(list(it.product((0,1), repeat = 2))): 
    this_ujk = ujk.copy()
    if x: this_ujk[T_x] *= -1
    if y: this_ujk[T_y] *= -1
    
    start_J, end_J = lines[highlighted_line]
    gap = gap_size_along_line(start_J, end_J, lattice, coloring, this_ujk)

    # phase_edge_t = pd.compute_phase_diagram(ts, gap, extra_args = {}, n_jobs = 7)
    gaps = np.array([gap(t) for t in ts])

    gap_vs_t[(1-2*x,1-2*y)] = gaps
    
data = dict(
    lines = lines,
    highlighted_line = highlighted_line,
    
    lattice = lattice,
    coloring = coloring,
    ujk = ujk,
    points = points,
    T_x = T_x,
    T_y = T_y,
    
    ts = ts,
    gap_vs_t = gap_vs_t,
)


with open("gap_along_lines.pickle", "wb") as f:
    pickle.dump(data, f)