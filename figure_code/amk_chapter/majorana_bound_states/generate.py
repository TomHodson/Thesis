#!/usr/bin/env python3
import numpy as np
import pickle

from koala import graph_utils as gu
from koala import example_graphs as eg
from koala import hamiltonian, flux_finder
from koala.flux_finder import pathfinding


J = np.array([1,1,1])
L = 50

rng = np.random.default_rng(498743987683476873498673)
lattice, colouring, ujk = eg.make_amorphous(L, rng = rng)
gs_flux_sector = flux_finder.fluxes_from_bonds(lattice, ujk)

a, b = gu.closest_plaquette(lattice, [0.33, 0.5]), gu.closest_plaquette(lattice, [0.66, 0.5])
plaqs, edges = pathfinding.path_between_plaquettes(lattice, a, b)
ujk[edges] *= -1 
flux_sector = flux_finder.fluxes_from_bonds(lattice, ujk)

H = hamiltonian.generate_majorana_hamiltonian(lattice, colouring, ujk, J)
eigs, vecs = np.linalg.eigh(H)

idx = np.argsort(np.abs(eigs))
lowest_wavefunction = vecs[:, idx[0]]

data = dict(
    L = L,
    lattice = lattice,
    colouring = colouring,
    gs_flux_sector = gs_flux_sector,
    flux_sector = flux_sector,
    plaquettes = (a, b),
    plaquette_path = plaqs,
    edge_path = edges,
    
    ujk = ujk,
    J = J,
    
    ground_state_density = np.abs(lowest_wavefunction)
)

with open("solved_lattice.pickle", "wb") as f:
    pickle.dump(data, f)