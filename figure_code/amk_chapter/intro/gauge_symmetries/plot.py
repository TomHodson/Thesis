#!/usr/bin/env python3
import matplotlib
from matplotlib.colors import to_rgba, to_hex
from matplotlib import cm
from matplotlib.collections import LineCollection
import matplotlib.gridspec as gridspec

import matplotlib.pyplot as plt
import numpy as np

from koala import plotting as pl
from koala import phase_diagrams as pd
from koala import flux_finder
from koala import example_graphs as eg
from koala.flux_finder import pathfinding
import pickle
import scipy.stats
from pathlib import Path
import itertools as it
import functools

w = column_width = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]

def multi_set_symmetric_difference(sets):
    return list(functools.reduce(lambda a,b: a^b, [set(s) for s in sets]))

def flood_iteration_plaquettes(l, plaquettes):
    return set(plaquettes) | set(it.chain.from_iterable(l.plaquettes[p].adjacent_plaquettes for p in plaquettes))

def flood_iteration_vertices(l, vertices):
    return set(vertices) | set(it.chain.from_iterable(i for v in set(vertices) for i in l.edges.indices[l.vertices.adjacent_edges[v]]))

def flood_vertices(l, vertices, n):
    for _ in range(n): vertices = flood_iteration_vertices(l, vertices)
    return vertices

w = column_width = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]
rng = np.random.default_rng(242535)
lattice, colouring, ujk = eg.make_honeycomb(13)
    
fig, ax = plt.subplots(nrows=1, ncols=1)
aspect_ratio = 3
fig.set_size_inches(2 * w, 2/aspect_ratio * w)


edges_to_highlight = []
vertices_to_highlight = []

# matplotlib.rcParams.update({'font.size': 10, 'text.usetex': False,})
# pl.plot_vertex_indices(lattice, ax = ax)
# pl.plot_edge_indices(lattice, ax = ax)
# pl.plot_plaquette_indices(lattice, ax = ax)

single_vertex = 56
vertices_to_highlight += [single_vertex, ]
edges_to_highlight += list(lattice.vertices.adjacent_edges[single_vertex])


multi_verts = [64,65,11,15]
vertices_to_highlight += multi_verts
edges_to_highlight +=  multi_set_symmetric_difference([lattice.vertices.adjacent_edges[v] for v in multi_verts])

seed = 80
vertices = flood_vertices(lattice, [seed, ], n = 3)
vertices_to_highlight += vertices
edges_to_highlight +=  multi_set_symmetric_difference([lattice.vertices.adjacent_edges[v] for v in vertices])

ps, edges = pathfinding.path_between_plaquettes(lattice, 75, 22)
# _, edges2 = pathfinding.path_between_plaquettes(lattice, 75, 12)
print(lattice.plaquettes[ps[-1]])
edges_to_highlight += edges + [621,543]

pl.plot_edges(lattice, color = 'grey', alpha = 0.5)
pl.plot_edges(lattice, subset = edges_to_highlight, color = 'k')
pl.plot_dual(lattice, subset = edges_to_highlight, color_scheme = line_colors[1:], alpha = 0.7)
pl.plot_vertices(lattice, subset = vertices_to_highlight, s = 7)

ax.set(xticks = [],
       yticks = [],
      xlim = (0,1),
      ylim = (0,1/aspect_ratio))

fig.tight_layout()
fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')