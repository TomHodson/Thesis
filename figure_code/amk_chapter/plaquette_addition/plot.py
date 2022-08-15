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
from koala import lattice

# imports just for this plot

column_width = 3.375
w = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

def transform_lattice(l, translate = np.array([0,0]), scale = 1):
    """
    Return a new lattice with vertex positions p' = (p*scale) + translate
    Does not attempt to deal with periodic boundary conditions
    """
    return lattice.Lattice(l.vertices.positions*scale + translate[None, :], l.edges.indices, l.edges.crossing)
    

fig, axes = plt.subplots(ncols = 2, figsize = (w*2, w))

ax = axes[1]
l = transform_lattice(eg.single_plaquette(6), scale = 0.5, translate = np.array([0,0.25]))
pl.plot_edges(l,ax = ax, directions = True, arrow_head_length = 0.04)

l1 = transform_lattice(l, translate = np.array([0.5, 0]))
pl.plot_edges(l1, ax = ax, directions = True, arrow_head_length = 0.04)

ax.axis("off")

ax = axes[0]
l = transform_lattice(eg.single_plaquette(6), scale = 0.5, translate = np.array([0,0.25]))
pl.plot_edges(l,ax = ax, directions = True, arrow_head_length = 0.04, subset = [0,1,2,3,5])
pl.plot_edges(l,ax = ax, subset = [4,], alpha = 0.4)


l1 = transform_lattice(l, translate = np.array([0.34, 0]))
pl.plot_edges(l1, ax = ax, directions = True, arrow_head_length = 0.04, subset = [0,2,3,4,5])
# pl.plot_edge_indices(l1, ax=ax)
ax.axis("off")

fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)