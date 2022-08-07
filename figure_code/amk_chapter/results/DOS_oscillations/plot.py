#!/usr/bin/env python3
import pickle
from pathlib import Path

import matplotlib
import matplotlib.gridspec as gridspec
import numpy as np
import scipy.stats
from koala import flux_finder
from koala import plotting as pl
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def find_transector(lattice, x = 0.5):
    points = []
    for l in [0.05,0.95]:
        dists = np.linalg.norm(lattice.vertices.positions - np.array([l, x]), axis = -1)
        m = np.argmin(dists)
        points.append(m)
    return flux_finder.path_between_vertices(lattice, points[0], points[1], early_stopping = False, maxits = 10**6)

def plot_DOS_oscillations(top_ax, bottom_ax):
    data_hlm_field = np.load('dos_oscillations_hlm_field.npy', allow_pickle=True).tolist()
    data_amo_nofield = np.load('dos_oscillations_am_nofield.npy', allow_pickle=True).tolist()
    xdata = np.load('xdata.npy')
    xdata = (xdata[:-1] + xdata[1:]) / 2.0

    system_sizes = data_amo_nofield.keys()
    line_colors = [matplotlib.cm.inferno(X) for X in [0.25, 0.5, 0.75]]
    
    for ax in [top_ax, bottom_ax]:
        ax.set(xscale = "log", yticks = [0.75, 1.00, 1.25, 1.50, 1.75, 2.00])


    for system_size, line_color in zip(system_sizes, line_colors):
      shared_args = {
        'c': line_color,
        'alpha': 0.7,
        'fmt': '.',
        'capsize': 2,
        'markersize': 2
      }

      hlm_vals = data_hlm_field[system_size]
      amo_vals = data_amo_nofield[system_size]

      top_ax.errorbar(
        xdata, hlm_vals[0], hlm_vals[1], label=f"$L={system_size}$", **shared_args
      )

      bottom_ax.errorbar(
        xdata, amo_vals[0], amo_vals[1], **shared_args
      )

    top_ax.legend(frameon = False, borderpad = 0.0, borderaxespad = 0.4, handletextpad = 0.2)

## Load data
with open("big_solved_lattice.pickle", "rb") as f:
    d = pickle.load(f)
    globals().update(d)
## Figure parameters
w = 3.375
rasterize = True #whether to rasterize some parts of the plots

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": 1})

## Set up the figure and the top level gridspec
# fig = plt.figure(figsize = (2 * w, w))
# gs = gridspec.GridSpec(nrows = 1, ncols = 2, figure=fig)
# left, right = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

fig, (left, right) = plt.subplots(ncols = 2, figsize = (2 * w, w/1.5), sharey = 'all')

### Right panel: DOS Oscillations
plot_DOS_oscillations(left, right)
left.text(0, 1.05, r"\textbf{(a)} Honeycomb + Magnetic Field", transform = left.transAxes, va = 'bottom', ha = 'left')
right.text(0, 1.05, r"\textbf{(b)} Amorphous w/o Magnetic Field", transform = right.transAxes, va = 'bottom', ha = 'left')

left.set(xlabel = "$E/J$", ylabel = r"DOS $\rho(E)$")
right.set(xlabel = "$E/J$")

# plt.subplots_adjust(bottom=0.15)
fig.tight_layout()

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')

