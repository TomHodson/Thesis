#!/usr/bin/env python3

import matplotlib
from matplotlib.colors import to_hex
from matplotlib import cm

import matplotlib.pyplot as plt
import numpy as np
import itertools as it
from pathlib import Path
import subprocess
from tqdm import tqdm

from koala import plotting as pl
from koala import phase_diagrams as pd
from koala import pointsets, voronization, flux_finder, graph_color
from koala import example_graphs as eg

import functools

def multi_set_symmetric_difference(sets):
    return list(functools.reduce(lambda a,b: a^b, [set(s) for s in sets]))

def flood_iteration_plaquettes(l, plaquettes):
    return set(plaquettes) | set(it.chain.from_iterable(l.plaquettes[p].adjacent_plaquettes for p in plaquettes))

def flood_iteration_vertices(l, vertices):
    return set(vertices) | set(it.chain.from_iterable(i for v in set(vertices) for i in l.edges.indices[l.vertices.adjacent_edges[v]]))


# imports just for this plot

column_width = 3.375
w = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]

# rng = np.random.default_rng(seed = 10)
# l, coloring, _ = eg.make_amorphous(8, rng = rng)
l, coloring, ujk = eg.make_honeycomb(8)

plaquettes = [40,]
vertices = [78,]

subprocess.run(["mkdir", "-p", "./animation"])

for n in tqdm(range(15)):
    fig, axes = plt.subplots(nrows=1, ncols=2)
    fig.set_size_inches(2 * w, 2/2 * w)
    for a in axes: a.set(xticks = [], yticks = [])

    # pl.plot_vertex_indices(l, ax = ax)
    # pl.plot_edge_indices(l, ax = ax)
    # pl.plot_plaquette_indices(l, ax = ax)
    
    if n > 0:
        vertices = flood_iteration_vertices(l, vertices)
        plaquettes = flood_iteration_plaquettes(l, plaquettes)
    
    ax = axes[0]
    
    multi_edges = multi_set_symmetric_difference([l.vertices.adjacent_edges[v] for v in vertices])
    
    if multi_edges: pl.plot_dual(l, ax = ax, color_scheme = line_colors[1:], subset = multi_edges)
    pl.plot_edges(l, ax = ax, color = 'k', subset = multi_edges)
    pl.plot_vertices(l, ax = ax, subset = list(vertices), s = 5)

    pl.plot_edges(l, ax = ax, alpha = 0.1)
    pl.plot_dual(l, ax = ax, color_scheme = line_colors[1:], alpha = 0.1)

    ax.set(xticks = [], yticks = [])
    
    ax = axes[1]

    plaquette_boolean = np.array([i in plaquettes for i in range(l.n_plaquettes)])

    fluxes = 1 - 2*plaquette_boolean
    ujk = flux_finder.find_flux_sector(l, fluxes, ujk)
    fluxes = flux_finder.fluxes_from_bonds(l, ujk)

    pl.plot_edges(l, ax = ax, alpha = 0.1)
    pl.plot_dual(l, ax = ax, color_scheme = line_colors[1:], alpha = 0.1)
    
    pl.plot_edges(l, ax = ax, subset = (ujk == -1))
    if len(plaquettes) > 1: pl.plot_dual(l, ax = ax, subset = (ujk == -1), color_scheme = line_colors[1:])
    pl.plot_plaquettes(l, subset = fluxes == -1, ax = ax, color_scheme = ["orange", "white"], alpha = 0.5);
    ax.set(xticks = [], yticks = [])
    
    fig.tight_layout()
    if n == 3: 
        fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)
        fig.savefig(f'./{Path.cwd().name}.pdf')
    fig.savefig(f"animation/iteration_{n:03}.svg")
    plt.close(fig)

subprocess.run(["magick", "animation/*.svg", f'./{Path.cwd().name}.gif'])
subprocess.run(["convert", "-delay", "100", f'./{Path.cwd().name}.gif', f'./{Path.cwd().name}.gif'])
subprocess.run(["rm", "-r", "./animation"])