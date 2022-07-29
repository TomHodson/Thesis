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

from koala import plotting as pl
from koala import phase_diagrams as pd
from koala import pointsets, voronization, flux_finder, graph_color
from koala import example_graphs as eg

# imports just for this plot
from scipy.spatial import Voronoi, voronoi_plot_2d

column_width = 3.375
w = 3.375
black_line_widths = 1.2

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

# Modified RGB color scheme
bond_colors = """" 
#e41a1c
#4daf4a
#00639a
""".split()[1:]

line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]

grid_style = dict(linewidths = black_line_widths, linestyle = '-', colors = 'k', alpha = 0.2)

cmap = plt.get_cmap("tab10")
color_scheme = cmap([0,1])

from koala.flux_finder import pathfinding
from koala.flux_finder.flux_finder import _greedy_plaquette_pairing
from koala.flux_finder.pathfinding import straight_line_length, periodic_straight_line_length
from koala.flux_finder.flux_finder import _flip_adjacent_fluxes

rng = np.random.default_rng(222424252565)
lattice, colouring, gs_ujk = eg.make_amorphous(8, rng = rng)
# random_ujk = rng.choice([+1, -1], size = gs_ujk.shape)
gs_fluxes = flux_finder.fluxes_from_bonds(lattice, gs_ujk)

better_ujk, better_fluxes = _flip_adjacent_fluxes(lattice, gs_ujk.copy(), gs_fluxes.copy())

def panel_a(ax):
    pl.plot_edges(lattice, ax = ax, directions = gs_ujk, linewidths = 1)
    pl.plot_plaquettes(lattice, labels = (gs_fluxes == +1), ax = ax, color_scheme = color_scheme, alpha = 0.5)
    
def panel_b(ax):
    
    def plaquette_metric(l):
        def d(a,b): return straight_line_length(l.plaquettes[a].center, l.plaquettes[b].center)
        return d

    def plot_bad_flux_pairing(l, bonds, fluxes, ax):
        bad_fluxes = np.nonzero(fluxes == -1)[0]
        pairs = _greedy_plaquette_pairing(bad_fluxes, distance_func = plaquette_metric(l))

        fluxes = flux_finder.fluxes_from_bonds(l, bonds)
        plaquette_labels = (fluxes == +1)
        pl.plot_plaquettes(l, plaquette_labels, color_scheme = color_scheme, ax = ax, alpha = 0.2)

        pl.plot_edges(l, alpha = 0.2, ax = ax)

        def pos(i): return l.plaquettes[i].center
        lines = [[pos(a),pos(b)] for a,b in pairs]

        from matplotlib.collections import LineCollection
        lines = LineCollection(lines, color = 'k')
        ax.add_collection(lines)

        return pairs
    
    return plot_bad_flux_pairing(lattice, better_ujk, better_fluxes, ax)

def panel_c(ax, pairs):
    path_kw = dict(heuristic = straight_line_length)
    
    def plot_paths(l, fluxes, pairs, ax):
        # pl.plot_plaquettes(l, fluxes == +1, color_scheme = color_scheme, ax = ax, alpha = 0.1)
        pl.plot_edges(l, alpha=0.2, ax = ax)

        plaquette_paths, edge_paths = zip(*(pathfinding.path_between_plaquettes(l, a, b, **path_kw) for a,b in pairs))

        for plaqs, edges in zip(plaquette_paths, edge_paths):
            color = cmap(rng.integers(10))
            pl.plot_plaquettes(l, subset=plaqs, color_scheme= [color,], ax=ax, alpha = 0.5)
            pl.plot_edges(l, subset=edges, color = 'black', ax=ax)

        return edge_paths
    plot_paths(lattice, better_fluxes, pairs, ax)
    
fig, axes = plt.subplots(nrows=1, ncols=3)
fig.set_size_inches(2 * w, 2/3 * w)

panel_a(axes[0])
pairs = panel_b(axes[1])
panel_c(axes[2], pairs)
for ax in axes: ax.set(xticks = [], yticks = [])

fig.tight_layout()
fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')