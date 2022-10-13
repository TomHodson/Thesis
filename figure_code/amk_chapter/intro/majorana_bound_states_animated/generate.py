#!/usr/bin/env python3
import numpy as np
import pickle
from time import time

from koala import example_graphs as eg
from koala import hamiltonian, flux_finder


J = np.array([1,1,1])
L = 50
rng = np.random.default_rng(498743987683476873498673)
print(f"Finding lattice with L = {L} plaquettes...")
t0 = time()
lattice, colouring, gs_ujk = eg.make_amorphous(L, rng = rng)
print(f"Found lattice in {(time() - t0):.0f} s")
gs_flux_sector = flux_finder.fluxes_from_bonds(lattice, gs_ujk)

data = dict(
    L = L,
    lattice = lattice,
    colouring = colouring,
    gs_flux_sector = gs_flux_sector,
    gs_ujk = gs_ujk,
    J = J,
)

print(f"Saving lattice with L = {L} plaquettes...")
with open("solved_lattice.pickle", "wb") as f:
    pickle.dump(data, f)