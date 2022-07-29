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

import functools

w = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

N = 2
fig, axes = plt.subplots(nrows=1, ncols=N)
fig.set_size_inches(2 * w, 2 * w / N)

def order_edges(l, edges, starting_edge = None):
    if starting_edge == None: starting_edge = edges[0]
    ordered_edges = [starting_edge,]
    directions = [1,]
    remaining_edges = set(edges) - set([starting_edge])
    print(l.edges.indices[starting_edge])
    final_vertex, current_vertex = l.edges.indices[starting_edge]
    # print(f"current_vertex: {current_vertex}, final_vertex: {final_vertex}")
    
    while current_vertex != final_vertex:
        # print(f"current_vertex: {current_vertex}")
        for edge in remaining_edges:
            # print(edge)
            if current_vertex in l.edges.indices[edge]:
                break
        else:
            print(f"couldn't find a connection for vertex {current_vertex}")
            return
        
        if current_vertex == l.edges.indices[edge][0]:
            directions.append(1)
            current_vertex = l.edges.indices[edge][1]
        else:
            directions.append(-1)
            current_vertex = l.edges.indices[edge][0]
        ordered_edges.append(edge)
        remaining_edges.remove(edge)
        
    return ordered_edges, directions
        

l, coloring, _ = eg.make_honeycomb(5)
plaquettes = [14,15,26,16,18,17]

# pl.plot_vertex_indices(l, ax = ax)
# pl.plot_edge_indices(l, ax = ax)
# pl.plot_plaquette_indices(l, ax = ax)

centerpoint = l.vertices.positions[30]
xc, yc = centerpoint
yc += 0.05
s = 0.37

ax = axes[0]

# ordered_W_p, directions = order_edges(l, W_p)
for i, p_i in enumerate(plaquettes):
    p = l.plaquettes[p_i]
    v = (p.center - centerpoint)*0.15
    translated_lattice = lattice.transform(l, translate = v)
    new_center = p.center + v
    
    pl.plot_edges(translated_lattice, ax = ax, subset = p.edges, directions = p.directions)
    ax.text(*new_center, f"$\phi_{i}$", ha= "center", va = "center")

ax.set(xticks = [], yticks = [], xlim = (xc-s,xc+s), ylim = (yc-s,yc+s))
ax.axis("off")

ax = axes[1]

plaquettes = [14,15,26,16,18,17]

all_contained_edges = list(functools.reduce(lambda a,b: a | b, [set(l.plaquettes[i].edges) for i in plaquettes]))
W_p = list(functools.reduce(lambda a,b: a^b, [set(l.plaquettes[i].edges) for i in plaquettes]))

ordered_W_p, directions = order_edges(l, W_p)
                  
pl.plot_edges(l, ax = ax, alpha = 0.2, subset = all_contained_edges)
pl.plot_edges(l, ax = ax, subset = ordered_W_p, label = "$W_p$", directions = directions)

ax.text(*centerpoint, f"$\phi_0 \phi_1 ...\phi_5$", ha= "center", va = "center")

ax.set(xticks = [], yticks = [], xlim = (xc-s,xc+s), ylim = (yc-s,yc+s))
ax.axis("off")

fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')