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

def closest_vertex(lattice, point):
    distances = np.linalg.norm(lattice.vertices.positions - np.array(point)[None, :], ord = 2, axis = -1)
    return np.argmin(distances)

def closest_plaquette(lattice, point):
    positions = np.array([p.center for p in lattice.plaquettes])
    distances = np.linalg.norm(positions - np.array(point)[None, :], ord = 2, axis = -1)
    return np.argmin(distances)

from koala.flux_finder import pathfinding

def round_the_back_metric(x = False, y = False):
    def length(a, b) -> float:
        delta = a - b
        if x: delta[0] = 1 - delta[0] 
        if y: delta[1] = 1 - delta[1] 
        return np.linalg.norm(delta, ord = 2)
    return length

def __loop(lattice, direction, kind):
    if kind == "graph":
        closest_thing = closest_vertex
        path = pathfinding.path_between_vertices
    elif kind == "dual":
        closest_thing = closest_plaquette
        path = pathfinding.path_between_plaquettes
    else: assert False
    
    points = np.array([[0.1, 0.5], [0.5, 0.5], [0.9, 0.5]])
    if direction == 'y': points = points[:, ::-1]
    a, b, c = [closest_thing(lattice, p) for p in points]
    heuristic = round_the_back_metric(x = (direction == 'x'), y = (direction == 'y'))

    t1, e1 = path(lattice, a, b)
    t2, e2 = path(lattice, b, c)
    t3, e3 = path(lattice, c, a, heuristic=heuristic)

    return np.concatenate([t1[:-1], t2[:-1], t3[:-1]]), np.concatenate([e1, e2, e3])
    
def graph_loop(lattice, direction = 'x'):
     return __loop(lattice, direction = direction, kind = "graph")
    
def dual_loop(lattice, direction = 'x'):
     return __loop(lattice, direction = direction, kind = "dual")
   
rng = np.random.default_rng(222424252565)
lattice, colouring, ujk_ground_state = eg.make_amorphous(8, rng = rng)    

ncols = 4
fig, axes = plt.subplots(nrows=1, ncols=ncols)
fig.set_size_inches(2 * w, 2/ncols * w)

for ax in axes: ax.set(xticks = [], yticks = [])

ax = axes[0]
v, e = graph_loop(lattice, direction = "x")
pl.plot_edges(lattice, ax = ax, linewidths = black_line_widths, color = 'grey')
pl.plot_edges(lattice, subset = e, ax = ax)

ax = axes[1]
v, e = graph_loop(lattice, direction = "y")
pl.plot_edges(lattice, ax = ax, linewidths = black_line_widths, color = 'grey')
pl.plot_edges(lattice, subset = e, ax = ax)

ax = axes[2]
p, e = dual_loop(lattice, direction = "x")
pl.plot_edges(lattice, ax = ax, linewidths = black_line_widths, color = 'grey')
pl.plot_plaquettes(lattice, ax = ax, subset = p, alpha = 0.5)
pl.plot_dual(lattice, subset = e, ax = ax)

ax = axes[3]
p, e = dual_loop(lattice, direction = "y")
pl.plot_edges(lattice, ax = ax, linewidths = black_line_widths, color = 'grey')
pl.plot_plaquettes(lattice, ax = ax, subset = p, alpha = 0.5)
pl.plot_dual(lattice, subset = e, ax = ax)


fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')

