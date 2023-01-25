#!/usr/bin/env python3 -u

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

subprocess.run(["mkdir", "-p", "./animation"])

## Generate points paths
rng = np.random.default_rng(426523462436)
N_time = 5
N_time_interp = 50
N_space = 20

t = np.linspace(0,1,N_time)
center = rng.random(size = (N_space, 2))[:, None, :] * np.ones((N_space, N_time, 2))
delta = 1 / np.sqrt(N_space) * rng.random(size = (N_space, N_time, 2))
points = (center + delta) % 1

points[:, -1, :] = points[:, 0, :] #make them start and end at the same point in time
from scipy.interpolate import make_interp_spline
interped_points = np.zeros(shape = (N_space, N_time_interp, 2), dtype = np.float64)
t_new = np.linspace(0, 1, N_time_interp)

for i in range(N_space):
    spl = make_interp_spline(t, points[i], bc_type = "periodic")
    interped_points[i] = spl(t_new)

def add_gridlines(ax):
    for v in voronization.generate_point_array(np.array(0), padding=1):
        voronization.plot_lines(ax, voronization.square + v[..., :], **grid_style)

def panel_a(ax, points):
    ax.set(xticks = [], yticks = [])
    ax.scatter(*points.T, s = 0.3, color = 'k')
    voronoi_plot_2d(voro, show_vertices = False, show_points  = False, ax = ax, line_width = black_line_widths)
    add_gridlines(ax)
    ax.set(xlim = (-margin,margin+1), ylim = (-margin,margin+1))

def panel_b(ax, points):
    ax.set(xticks = [], yticks = [])
    voronization.generate_lattice(points, shift_vertices = False, debug_plot = ax)#, linewidth = black_line_widths)
    add_gridlines(ax)
    ax.set(xlim = (-margin,margin+1), ylim = (-margin,margin+1))

def panel_c(ax, lattice):
    ax.set(xticks = [], yticks = [])
    pl.plot_edges(lattice, ax = ax, color_scheme = ['k'])
    ax.fill_between(x = (-margin, 0), y1 = (1,1), color = "white", zorder = 2)
    ax.fill_between(x = (1, 1+margin), y1 = (1,1), color = "white", zorder = 2)
    ax.fill_betweenx(y = (-margin, 0), x1 = (-margin,-margin), x2 = (1+margin,1+margin), color = "white", zorder = 2)
    ax.fill_betweenx(y = (1, 1+margin), x1 = (-margin,-margin), x2 = (1+margin,1+margin), color = "white", zorder = 2)
    ax.axis("off")

    unit_cell = matplotlib.patches.Polygon(((0,0), (0,1), (1,1), (1,0)), edgecolor = 'k', facecolor = "None", linewidth = black_line_widths, zorder = 3)
    ax.add_artist(unit_cell)
    ax.set(xlim = (-margin,margin+1), ylim = (-margin,margin+1))

interped_points = interped_points % 1

for i in tqdm(range(N_time_interp)):
    points = interped_points[:, i, :]
    voro = Voronoi(points)
    lattice = voronization.generate_lattice(points, shift_vertices = False)
    # coloring = graph_color.color_lattice(lattice)

    fig, axes = plt.subplots(nrows=1, ncols=3)
    fig.set_size_inches(2 * w, 2/3 * w)
    panel_a(axes[0], points)
    panel_b(axes[1], points)
    panel_c(axes[2], lattice)


    fig.tight_layout()

    if i == 0: 
        fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)
        fig.savefig(f'./{Path.cwd().name}.pdf')
    fig.savefig(f"animation/iteration_{i:03}.svg")
    plt.close(fig)

print("Making the gif...")
subprocess.run(["magick", "animation/*.svg", f'./{Path.cwd().name}.gif'])
subprocess.run(["rm", "-r", "./animation"])
