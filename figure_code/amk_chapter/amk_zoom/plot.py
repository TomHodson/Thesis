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
import pickle
import scipy.stats
from pathlib import Path

column_width = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]
print(line_colors)

with open('./lattice.pickle', 'rb') as f:
    globals().update(**pickle.load(f))

w = 3.375

fig, ax = plt.subplots(nrows=1, ncols=3)

fig.set_size_inches(2 * w, 2/3 * w)

# ax[0].axis('off')
# ax[1].axis('off')
# ax[2].axis('off')

for a in ax: 
    a.set(xticks = [], yticks = [])

pl.plot_edges(lattice, labels=coloring, color_scheme=line_colors, ax=ax[0], linewidth = 0.9, zorder = -1)
pl.plot_edges(lattice, labels=coloring, color_scheme=line_colors, ax=ax[1], 
            directions = True,
            arrow_head_length = 0.01,
            zorder = -1,
            )


# plt.tight_layout()
plt.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

######### Code to draw the zoom lines ################
line_args = dict(linewidth = black_line_widths , color = 'k')
width = 0.2

from matplotlib.patches import Rectangle
from matplotlib import lines

def datacoords_to_fig(fig, ax, point): 
    trans = ax.transData + fig.transFigure.inverted()
    return trans.transform_point(point) #transform to figure coords

def rect_to_rect(fig, ax0, ax1, xy, width):
    x,y = xy

    #set the limits for the second axis
    ax1.set_xlim([x-width/2, x+width/2])
    ax1.set_ylim([y-width/2, y+width/2])

    r = Rectangle(xy = (x-width/2, y-width/2),
    width = width, height = width, fill = False, **line_args)
    ax0.add_patch(r)

    for s in [+1, -1]:
        (x0, y0) = datacoords_to_fig(fig, ax0, (x+width/2, y + s*width/2))
        (x1, y1) = datacoords_to_fig(fig, ax1, (x-width/2, y + s*width/2))
        fig.add_artist(lines.Line2D([x0, x1], [y0, y1], **line_args))

rect_to_rect(fig, ax[0], ax[1], xy = (0.5, 0.5), width = width)

#find the closest vertex to the center to center the box on
dists = np.linalg.norm(lattice.vertices.positions - np.array([0.5, 0.5]), axis = -1)
closest_vertex_i = np.argmin(dists)
closest_vertex = lattice.vertices.positions[closest_vertex_i]

pl.plot_edges(lattice, labels=coloring, color_scheme=line_colors, ax=ax[2], linewidth = 0.9)
width = 0.02
rect_to_rect(fig, ax[1], ax[2], xy = closest_vertex, width = width)

##### phase diagram plotting



def project_to_triangle(points): 
    skew = np.array([[1, np.cos(np.pi/3)],
                          [0, np.sin(np.pi/3)]])

    return np.einsum('ij,kj -> ki', skew, points[..., :2])

def plot_phase_diagram(ax):
    with open('critical_line_1.pickle', 'rb') as f:
        lines, phase_edge_t = pickle.load(f)
    
    edge_t = phase_edge_t.T
    sterr = scipy.stats.sem(edge_t, axis = 0)
    tbar = np.mean(edge_t, axis = 0)
    low = tbar - sterr
    high = tbar + sterr

    pd.plot_triangle(ax)

    points = lines[:, 0] * (1 - tbar)[:, None] + lines[:, 1] * tbar[:, None]

    # ax.plot(*project_to_triangle(points).T)
    triangle_points = np.array([[0,0], [np.cos(np.pi/3),np.sin(np.pi/3)], [1,0]])

    triangle = matplotlib.patches.Polygon(triangle_points, closed=True, color = 'purple')
    ax.add_artist(triangle)

    chiral_phase = matplotlib.patches.Polygon(project_to_triangle(points), closed=True, color = 'orange')
    ax.add_artist(chiral_phase)

    ax.axis('off')
    
plot_phase_diagram(ax[2])

##### end phase diagram plotting

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')