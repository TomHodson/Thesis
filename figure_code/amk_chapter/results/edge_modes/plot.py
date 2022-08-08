#!/usr/bin/env python3
import pickle

import matplotlib
import matplotlib.gridspec as gridspec
import numpy as np
import scipy.stats
from koala import flux_finder
from koala import plotting as pl
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from pathlib import Path


def find_transector(lattice, x = 0.5):
    points = []
    for l in [0.05,0.95]:
        dists = np.linalg.norm(lattice.vertices.positions - np.array([l, x]), axis = -1)
        m = np.argmin(dists)
        points.append(m)
    return flux_finder.path_between_vertices(lattice, points[0], points[1], early_stopping = False, maxits = 10**6)


## Setup colormap
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

## Load data
with open("big_solved_lattice.pickle", "rb") as f:
    d = pickle.load(f)
    print(d.keys())
    globals().update(d)

DOS, E_bins = np.histogram(energies, bins = 300)
IPR, _, _ = scipy.stats.binned_statistic(energies, raw_IPR, statistic='mean', bins = E_bins)

## Figure parameters
column_width = w = 3.375
rasterize = True #whether to rasterize some parts of the plots
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": 1})

# gridspec inside gridspec
fig = plt.figure()
fig.set_size_inches(2*w,w/(3/2))
gs = gridspec.GridSpec(1, 2, figure=fig, wspace = 0.3, width_ratios = (1,2))

left_gs = gs[0].subgridspec(2, 1, hspace = 0, height_ratios = (8,2))
right_gs = gs[1].subgridspec(2, 2, hspace = 0.0, width_ratios = (15,1), wspace = 0.05)

gs = left_gs
edge_mode_ax = fig.add_subplot(gs[0])
edge_mode_transect_ax = fig.add_subplot(gs[1])

gs = right_gs
DOS_colorbar_ax = fig.add_subplot(gs[:, 1])
open_bc_DOS_ax = fig.add_subplot(gs[0, 0])
closed_bc_DOS_ax = fig.add_subplot(gs[1, 0])

edge_mode_ax.set(yticks = [])

### DOS plot

ax = open_bc_DOS_ax
cmap = inferno_purple_to_white_cmap
color_val = np.log(IPR)
color_val = (color_val - np.min(color_val)) / (np.max(color_val) - np.min(color_val))
norm = matplotlib.colors.Normalize(vmin = 0, vmax = 0.6)
IPR_color = cmap(norm(color_val))

ax.set(ylabel = "DOS", xticks = [], xlim = (-0.4, 0.4))
ax.bar(E_bins[:-1], DOS, width = np.diff(E_bins), align = "edge", color = IPR_color, zorder = -1)
if rasterize: ax.set_rasterization_zorder(0)
print(f"Edge state energy = {energies[edge_state_i]}")
# ax.hist(energies, bins = 100, orientation = 'horizontal')
ax.text(0.0, 20, r"\textbf{(b)}", ha = 'center')

ax = closed_bc_DOS_ax
ax.set(xlabel = "Energy $E/J$", ylabel = "DOS", ylim = (0,25), xlim = (-0.2, 0.2))
ax.text(0.0, 20, r"\textbf{(c)}", ha = 'center')

ax = DOS_colorbar_ax
fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation = "vertical")
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
ax.set_ylabel("log(IPR)", fontsize=11)
# ax.set(yticks = [])

### Main edge mode plot
ax = edge_mode_ax
path_verts, path_edges = find_transector(lattice)
pl.plot_edges(lattice, linewidth = 0.2, ax = ax, zorder = -1, alpha = 0.5)
pl.plot_edges(lattice, subset = path_edges, linewidth = 1, ax = ax)
ax.tripcolor(*lattice.vertices.positions.T, edge_state_density,
             cmap = plum_to_white_cmap, shading = 'gouraud', vmin = 0.001, vmax = 0.01, zorder = -2)

ax.text(-0.01, 0.99, r"\textbf{(a)}", ha = 'right', va = 'top')

if rasterize: ax.set_rasterization_zorder(0)


p = 0.01
ax.set(xticks = [], yticks = [], xlim = [p,1-p], ylim = [p,1-p])

### Edge mode line cut
ax = edge_mode_transect_ax
n_steps = len(path_verts)
x = np.arange(n_steps) - n_steps//2
ax.plot(x, np.log(edge_state_density)[path_verts], linewidth = 1, color = 'k', solid_capstyle='round')
ax.set(yticks = [], xlabel = "Lattice distance")

# plt.subplots_adjust(hspace=.0, right=0.88, bottom=0.15)

fig.savefig(f'./{Path.cwd().name}.pdf', dpi = 400)
fig.savefig(f'./{Path.cwd().name}.svg', dpi = 400)

