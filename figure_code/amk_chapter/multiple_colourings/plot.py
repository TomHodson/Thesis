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

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.expanduser('~/git/Thesis/figure_code')))
from plot_settings import bond_colors, plaq_color_scheme, dual_color

grid_style = dict(linewidths = black_line_widths, linestyle = '-', colors = 'k', alpha = 0.2)

margin = 0.2 # how much of the other unit cells to show

fig, axes = plt.subplots(nrows=1, ncols=3)
fig.set_size_inches(2 * w, 2/3 * w)

## Computations
n_points = 20
rng = np.random.default_rng(4242423)
points = rng.uniform(size=(n_points,2))
voro = Voronoi(points)
lattice = voronization.generate_lattice(points, shift_vertices = False)
# coloring = graph_color.color_lattice(lattice)
solveable, colorings = graph_color.edge_color(lattice, n_colors = 3, n_solutions = 3)
# gs_flux_sector = np.array([eg.ground_state_ansatz(p.n_sides) for p in lattice.plaquettes], dtype = np.int8)
# ujk = flux_finder.find_flux_sector(lattice, gs_flux_sector)


def panel(ax, coloring, highlight):
    ax.set(xticks = [], yticks = [])
    pl.plot_edges(lattice, ax = ax, labels = coloring, color_scheme = bond_colors, alpha = 0.3)
    pl.plot_edges(lattice, ax = ax, subset = highlight, labels = coloring, color_scheme = bond_colors)
    

colorings = list(colorings)
base = colorings[0]
diffs = [np.where(coloring != base)[0] for coloring in colorings]
diffs[0] = np.arange(lattice.n_edges, dtype = int)

for ax, coloring, diff in zip(axes, colorings, diffs):
    panel(ax, coloring, highlight = diff)


fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)

