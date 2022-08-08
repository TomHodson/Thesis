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

column_width = w = 3.375
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

ncols = 2
fig, axes = plt.subplots(nrows=1, ncols=ncols)
fig.set_size_inches(2 * w, 2/ncols * w)

flux_sector = flux_finder.fluxes_from_bonds(lattice, ujk)

ax = axes[0]
pl.plot_edges(lattice, linewidth = 1, ax = ax, zorder = -1, alpha = 0.5)
pl.plot_plaquettes(lattice, subset = flux_sector != gs_flux_sector, ax = ax)
pl.plot_dual(lattice, subset = edge_path, linewidth = 2, ax = ax,
             color_scheme = bond_colors, zorder = 1)
ax.set_rasterization_zorder(0)

ax = axes[1]
pl.plot_edges(lattice, linewidth = 0.2, ax = ax, zorder = -1, alpha = 0.5)

ax.tripcolor(*lattice.vertices.positions.T, ground_state_density,
             cmap = plum_to_white_cmap,
             # cmap = 'inferno',
             shading = 'gouraud', 
             vmin = 0.001, vmax = 0.1,
             zorder = -2)

ax.set_rasterization_zorder(0)
for ax in axes: ax.set(xticks = [], yticks = [])

fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')

