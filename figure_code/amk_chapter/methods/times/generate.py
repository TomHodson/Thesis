#!/usr/bin/env python3
from time import time
import pickle
import numpy as np
from matplotlib import pyplot as plt
from tqdm.notebook import tqdm

from koala import voronization, graph_color, flux_finder, \
        hamiltonian,  phase_diagrams, \
        example_graphs

def test(L):
    t = []
    t.append(time())
    points = np.random.uniform(size=(L,2))
    lattice = voronization.generate_lattice(points)
    t.append(time())
    coloring = graph_color.color_lattice(lattice)
    t.append(time())
    gs_flux_sector = np.array([example_graphs.ground_state_ansatz(p.n_sides) for p in lattice.plaquettes], dtype = np.int8)
    ujk = flux_finder.find_flux_sector(lattice, gs_flux_sector)
    t.append(time())
    ham = hamiltonian.generate_majorana_hamiltonian(lattice, coloring, ujk, J = np.array([1,1,1]))
    eigs, vecs = np.linalg.eigh(ham)
    t.append(time())
    return np.diff(np.array(t))

periods = [
        "Voronise points",
        "Color lattice",
        "Compute Ground State ujk",
        "Diagonalise Hamiltonian",
]
Ls = np.arange(100, 1000, 100)
# ts = phase_diagrams.compute_phase_diagram(Ls, test, extra_args = {}, n_jobs = 1, progress_bar = False)
def do_tests(Ls):
    for L in Ls:
        print(f"working on {L}")
        yield test(L)

ts = np.array([t for t in do_tests(Ls)]).T

data = dict(
        periods = periods,
        ts = ts,
        Ls = Ls,
)

with open("lattice_generation_times.pickle", 'wb') as f:
    pickle.dump(data, f)