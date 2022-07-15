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
import custom_voronization as voronization
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

margin = 0.2 # how much of the other unit cells to show

fig, axes = plt.subplots(nrows=1, ncols=3)
fig.set_size_inches(2 * w, 2/3 * w)

## Computations
n_points = 20
rng = np.random.default_rng(4242423)
points = rng.uniform(size=(n_points,2))
voro = Voronoi(points)
lattice = voronization.generate_lattice(points, shift_vertices = False)
coloring = graph_color.color_lattice(lattice)
# gs_flux_sector = np.array([eg.ground_state_ansatz(p.n_sides) for p in lattice.plaquettes], dtype = np.int8)
# ujk = flux_finder.find_flux_sector(lattice, gs_flux_sector)

def add_gridlines(ax):
    for v in voronization.generate_point_array(np.array(0), padding=1):
        voronization.plot_lines(ax, voronization.square + v[..., :], **grid_style)

def panel_a(ax):
    ax.set(xticks = [], yticks = [])
    ax.scatter(*points.T, s = 0.3, color = 'k')
    voronoi_plot_2d(voro, show_vertices = False, show_points  = False, ax = ax, line_width = black_line_widths)
    add_gridlines(ax)
    ax.set(xlim = (-margin,margin+1), ylim = (-margin,margin+1))

def panel_b(ax):
    ax.set(xticks = [], yticks = [])
    voronization.generate_lattice(points, shift_vertices = False, debug_plot = ax, linewidth = black_line_widths)
    add_gridlines(ax)
    ax.set(xlim = (-margin,margin+1), ylim = (-margin,margin+1))

def panel_c(ax):
    ax.set(xticks = [], yticks = [])
    pl.plot_edges(lattice, ax = ax, labels = coloring, color_scheme = bond_colors)
    ax.fill_between(x = (-margin, 0), y1 = (1,1), color = "white", zorder = 2)
    ax.fill_between(x = (1, 1+margin), y1 = (1,1), color = "white", zorder = 2)
    ax.fill_betweenx(y = (-margin, 0), x1 = (-margin,-margin), x2 = (1+margin,1+margin), color = "white", zorder = 2)
    ax.fill_betweenx(y = (1, 1+margin), x1 = (-margin,-margin), x2 = (1+margin,1+margin), color = "white", zorder = 2)
    ax.axis("off")

    unit_cell = matplotlib.patches.Polygon(((0,0), (0,1), (1,1), (1,0)), edgecolor = 'k', facecolor = "None", linewidth = black_line_widths, zorder = 3)
    ax.add_artist(unit_cell)
    ax.set(xlim = (-margin,margin+1), ylim = (-margin,margin+1))


panel_a(axes[0])
panel_b(axes[1])
panel_c(axes[2])


fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')

# for i, panel in enumerate([panel_a, panel_b, panel_c]):
#     fig, ax = plt.subplots()
#     fig.set_size_inches(2*w/3, 2*w/3)
#     panel(ax)
#     fig.tight_layout()

#     Path('individual_panels').mkdir(exist_ok = True)
#     fig.savefig(f'individual_panels/{Path.cwd().name}_axis{i}.svg')
#     fig.savefig(f'individual_panels/{Path.cwd().name}_axis{i}.pdf')

