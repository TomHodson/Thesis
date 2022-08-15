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

column_width = 3.375
w = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

Ns= [3,4,5,6,7]

fig, axes = plt.subplots(nrows=1, ncols=len(Ns))
fig.set_size_inches(2 * w, 2 * w / len(Ns))

for n, ax in zip(Ns, axes):
    l = eg.single_plaquette(n)
    pl.plot_edges(l,ax = ax, directions = True, arrow_head_length=0.05)
    ax.text(0.5,0.5, r"$\pm i$" if n%2 else r"$\pm 1$", ha = "center", va = "center", fontsize = 16)
    s = 0.10
    ax.set(xlim = (s,1-s), ylim = (s, 1-s))
    ax.axis("off")

fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)