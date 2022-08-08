#!/usr/bin/env python3
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1" 
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

data = dict()

import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
import pickle

from koala import chern_number as cn
from koala import example_graphs as eg
from koala import phase_diagrams as pd
from koala import plotting as pl
from koala import flux_finder
from koala import hamiltonian

from koala.lattice import cut_boundaries
from koala import graph_color as gc

def chern_number_from_crosshair_marker(lattice, coloring, ujk, J, 
                                       marker = "crosshair", radius = 0.25):
    
    H_maj = hamiltonian.generate_majorana_hamiltonian(lattice, coloring, ujk, J)
    eigs, vecs = np.linalg.eigh(H_maj)
    lowest_diag = np.array([1]*(lattice.n_vertices//2) + [0]*(lattice.n_vertices//2) )
    P = vecs @ np.diag(lowest_diag) @ vecs.conj().T
    marker_position = np.array([0.5,0.5])
    
    if marker == "crosshair":
        marker = cn.crosshair_marker(lattice, P, marker_position)
    elif marker == "chern":
        marker = cn.chern_marker(lattice, P)
    else:
        print(f"Unknown marker {marker}")
        return
    
    def sites(r): return np.sqrt(np.sum((lattice.vertices.positions - marker_position)**2, axis=1)) <= r
    
    if isinstance(radius, np.ndarray):
        return np.array([np.sum(marker[sites(r)]) for r in radius])
    
    return np.sum(marker[sites(radius)])

J = np.array([1,1,1])
radius = 0.3
N = 25 #how many plaquettes the lattice should have

symmetric = True #how to do the phase diagram
samples = 30 # how dense to make the samples for the phase diagram


if __name__ == '__main__':
    print(f"Construting lattice with {N} plaquettes...")
    lattice, _, _ = eg.make_amorphous(N)
    lattice = cut_boundaries(lattice)
    coloring = gc.color_lattice(lattice)
    gs_flux_sector = np.array([eg.ground_state_ansatz(p.n_sides) for p in lattice.plaquettes])
    ujk = flux_finder.find_flux_sector(lattice, gs_flux_sector)

    print(f"Diagonalising...")
    H_maj = hamiltonian.generate_majorana_hamiltonian(lattice, coloring, ujk, J)
    eigs, vecs = np.linalg.eigh(H_maj)
    lowest_diag = np.array([1]*(lattice.n_vertices//2) + [0]*(lattice.n_vertices//2) )
    P = vecs @ np.diag(lowest_diag) @ vecs.conj().T

    print(f"Computing Markers...")
    crosshair_position = np.array([0.5,0.5])
    crosshair_marker = cn.crosshair_marker(lattice, P, crosshair_position)
    chern_marker = cn.chern_marker(lattice, P)

    plot1 = dict(
            radius = radius,
            lattice = lattice,
            coloring = coloring, 

            crosshair_position = crosshair_position,
            crosshair_marker = crosshair_marker,
            chern_marker = chern_marker,
        )
    data['plot1'] = plot1

    print("Computing Markers as a function of radius...")
    radii = np.linspace(0.05,0.8,100)

    J_non_abelian = np.array([1,1,1])
    non_abelian = chern_number_from_crosshair_marker(lattice, coloring, ujk, 
                                        J = J_non_abelian, 
                                        marker = "crosshair", radius = radii)
    J_abelian = np.array([0.25, 0.25, 1])
    abelian = chern_number_from_crosshair_marker(lattice, coloring, ujk, 
                                        J = J_abelian, 
                                        marker = "crosshair", radius = radii)

    plot2 = dict(
        radii = radii,
        J_non_abelian = J_non_abelian,
        non_abelian = non_abelian,
        J_abelian = J_abelian,
        abelian = abelian,
    )
    data['plot2'] = plot2

    if symmetric: sampling_points, triangulation = pd.get_triangular_sampling_points(samples = samples)
    else: sampling_points, triangulation = pd.get_non_symmetric_triangular_sampling_points(samples = samples)

    def function(J, lattice, coloring, ujk):
        return chern_number_from_crosshair_marker(lattice, coloring, ujk, 
                        J = J, 
                        marker = "crosshair", radius = radius)


    extra_args = dict(lattice = lattice,
                    coloring = coloring,
                    ujk = ujk)

    print("Computing Phase Diagram...")
    # crosshair_phase_diagram = pd.compute_phase_diagram(sampling_points, function, extra_args, n_jobs = 2)
    crosshair_phase_diagram = np.zeros(shape = len(sampling_points), dtype = float)
    for i, J in tqdm(list(enumerate(sampling_points))):
        crosshair_phase_diagram[i] = function(J, lattice, coloring, ujk)


    plot3 = dict(
        symmetric = symmetric,
        sampling_points = sampling_points,
        crosshair_phase_diagram =crosshair_phase_diagram,
    )

    data['plot3'] = plot3

    import pickle
    with open("chern_number_phase_diagram.pickle", "wb") as f:
        pickle.dump(data, f)