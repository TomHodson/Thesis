#!/usr/bin/env python3

import matplotlib
from matplotlib.colors import to_rgba, to_hex
from matplotlib import cm
from matplotlib.collections import LineCollection
import matplotlib.gridspec as gridspec

import matplotlib.pyplot as plt
import numpy as np
import pickle
import scipy.stats
from pathlib import Path
import subprocess
from tqdm import tqdm

from koala import plotting as pl
from koala import phase_diagrams as pd
from koala import pointsets, voronization, flux_finder, graph_color, hamiltonian
from koala import example_graphs as eg
from koala import graph_utils as gu
from koala.flux_finder import pathfinding

# imports just for this plot
from scipy.spatial import Voronoi, voronoi_plot_2d

column_width = w = 3.375
black_line_widths = 1.2

from matplotlib.colors import ListedColormap

with open("solved_lattice.pickle", "rb") as f:
    data = pickle.load(f)
    globals().update(data)


inferno = matplotlib.cm.get_cmap('inferno_r', 256)
newcolors = inferno(np.linspace(0.7, 0, 256))
white = np.array([1, 1, 1, 1])
newcolors[-1, :] = white
inferno_purple_to_white_cmap = ListedColormap(newcolors)

purple = inferno(0.5)
white = np.array([1,1,1,1])
t = np.linspace(0, 1, 256)[:, None]
newcolors = t * purple + (1-t) * white
plum_to_white_cmap = ListedColormap(newcolors)

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.expanduser('~/git/Thesis/figure_code')))
from plot_settings import bond_colors, plaq_color_scheme, dual_color

def compute_positions(t):
    "compute plaquette positions at a function of t in [0,1]"
    s, c = np.sin(2*np.pi * t), np.cos(2*np.pi * t)
    r = 0.4 * np.abs(np.cos(4*np.pi * t))
    p1 = (0.5 - r*c, 0.5 + r*s)
    p2 = (0.5 + r*c, 0.5 - r*s)
    return p1, p2

def compute_ground_state_density(t, v0 = None):
    #compute positions for the plaquettes based on which frame wer're on
    p1, p2 = compute_positions(t)
    #compute the plaquette indices and a path between them
    vortices = gu.closest_plaquette(lattice, p1), gu.closest_plaquette(lattice, p2)
    ujk = gs_ujk.copy()

    if vortices[0] != vortices[1]: #if there are two vortices 
        plaqs, edge_path = pathfinding.path_between_plaquettes(lattice, *vortices)
        ujk[edge_path] *= -1 
    else:
        edge_path = []

    #lattice, colouring and J come from the global scope because they're fixed
    H = hamiltonian.generate_majorana_hamiltonian(lattice, colouring, ujk, J)
    eigs, vecs = scipy.sparse.linalg.eigsh(H, k=1, sigma=0, v0 = v0)
    v0 = vecs[:, 0]
    lowest_wavefunction = vecs[:, 0]
    
    return vortices, edge_path, lowest_wavefunction, v0

def plot_it(i, interp_t, 
            vortices, edge_path,
            next_vortices, next_edge_path,
            ground_state_density, static_thumbnail = False):
    ncols = 2
    fig, axes = plt.subplots(nrows=1, ncols=ncols)
    fig.set_size_inches(2 * w, 2/ncols * w)

    ax = axes[0]
    pl.plot_edges(lattice, linewidth = 1, ax = ax, zorder = -1, alpha = 0.5)
    
    for v, ep, t in [[vortices, edge_path, 1 - interp_t], [next_vortices, next_edge_path, interp_t]]:
        pl.plot_plaquettes(lattice, subset = list(v), ax = ax, color_scheme = dual_color, alpha = t)
        if ep: pl.plot_dual(lattice, subset = ep, linewidth = 2, ax = ax,
                    color_scheme = dual_color, zorder = 1, alpha = t)
    ax.set_rasterization_zorder(0)
    
    ax = axes[1]

    pl.plot_edges(lattice, linewidth = 0.2, ax = ax, zorder = -1, alpha = 0.5)

    if ep: ax.tripcolor(*lattice.vertices.positions.T, ground_state_density,
                cmap = plum_to_white_cmap,
                # cmap = 'inferno',
                shading = 'gouraud', 
                vmin = 0.001, vmax = 0.1,
                zorder = -2)

    ax.set_rasterization_zorder(0)
    for ax in axes: ax.set(xticks = [], yticks = [])
    fig.tight_layout()

    if static_thumbnail: 
        fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)
        fig.savefig(f'./{Path.cwd().name}.pdf')

    fig.savefig(f"animation/iteration_{i:03}.svg")
    plt.close(fig)

rng = np.random.default_rng(222424252565)

subprocess.run(["mkdir", "-p", "./animation"])

N_keyframes = 60 #how many times to actually diagonalise the matrix
N_interpolation_frames = 1 #how many interpolation frames to add in between
N = N_keyframes * N_interpolation_frames

#generate a random starting vector to start but later use the previous one
v0 = np.random.rand(lattice.n_vertices)

*next_solution, v0 = compute_ground_state_density(t = 0, v0 = v0)
for keyframe_i in tqdm(range(N_keyframes)):
    #we need to compute a new keyframe
    t = (keyframe_i + 1) / N_keyframes
    current_solution = next_solution
    *next_solution, v0 = compute_ground_state_density(t, v0 = v0)

    for interp_i in tqdm(range(N_interpolation_frames)):
        interp_t = interp_i / N_interpolation_frames

        vortices, edge_path, wavefunction = current_solution
        next_vortices, next_edge_path, next_wavefunction = next_solution

        s, c = np.sin(np.pi/2 * interp_t), np.cos(np.pi/2 * interp_t)
        interped_wavefunction = c * wavefunction + s * next_wavefunction
        interped_ground_state_density = np.abs(interped_wavefunction)

        i = keyframe_i * N_interpolation_frames + interp_i
        plot_it(i, interp_t, 
            vortices, edge_path,
            next_vortices, next_edge_path,
            interped_ground_state_density,
            static_thumbnail = (i == 0))

print("Making the gif...")
subprocess.run(["magick", "animation/*.svg", f'./{Path.cwd().name}.gif'])
subprocess.run(["convert", "-delay", "20", f'./{Path.cwd().name}.gif', f'./{Path.cwd().name}.gif'])
subprocess.run(["rm", "-r", "./animation"])


