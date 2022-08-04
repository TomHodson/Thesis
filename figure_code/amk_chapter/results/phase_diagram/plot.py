#!/usr/bin/env python3

import matplotlib
from matplotlib.colors import to_rgba, to_hex
from matplotlib import cm
from matplotlib.patches import Polygon

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import pickle
from pathlib import Path

from koala import phase_diagrams as pd

# imports just for this plot

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

chiral_phase_color = to_hex(cm.inferno(0.75))
line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]

with open("gap_along_lines.pickle", "rb") as f:
    data = pickle.load(f)
    lines, highlighted_line, lattice, coloring, ujk, points, T_x, T_y, ts, gap_vs_t = data.values()

def project_to_triangle(points): 
    skew = np.array([[1, np.cos(np.pi/3)],
                          [0, np.sin(np.pi/3)]])

    return np.einsum('ij,kj -> ki', skew, points[..., :2])
    
def line(start, end, npoints):
    t = np.linspace(0,1,npoints)[:, None]
    return start * (1-t) + end * t

ncols = 3
fig, axes = plt.subplots(nrows=1, ncols=ncols)
fig.set_size_inches(2 * w, 2/ncols * w)

ax = axes[1]
for i, (s, e) in enumerate(lines):
    p = line(s, e, npoints = 20)
    ax.plot(*project_to_triangle(p).T, 
            color = 'r' if i == highlighted_line else 'k')
    
ax.axis('off')
pd.plot_triangle(ax)
triangle_points = np.array([[0,0], [np.cos(np.pi/3),np.sin(np.pi/3)], [1,0]])
ax.text(*triangle_points[0], "$J_x$", va = "top", ha = "right")
ax.text(*triangle_points[1] + [0,0.01], "$J_y$", va = "bottom", ha = "center")
ax.text(*triangle_points[2], "$J_z$", va = "top", ha = "left")


# ax = axes[1]
# pl.plot_edges(lattice, ax = ax, alpha = 0.5)
# pl.plot_edges(lattice, ax = ax, subset = list(set(T_x) | set(T_y)))

ax = axes[0]

for sector, gaps in gap_vs_t.items():
    ax.plot(ts, gaps, label = f"{sector}")
ax.set(ylabel = "Fermion Gap", xlabel = "Proportional Distance (t)")
    
ax.set(xlim = (0.6, 1))
# ax.legend()

# ax = axes[2]
# ax.axis('off')
# pd.plot_triangle(ax)
# ax.set(xlim = axes[1].get_xlim(), ylim = axes[1].get_ylim())

for ax in axes[[1,2]]: ax.set(xticks = [], yticks = [])

def plot_phase_diagram(ax):
    with open('critical_line_1.pickle', 'rb') as f:
        lines, phase_edge_t = pickle.load(f)
    
    edge_t = phase_edge_t.T
    tbar = np.mean(edge_t, axis = 0)

    pd.plot_triangle(ax)

    points = lines[:, 0] * (1 - tbar)[:, None] + lines[:, 1] * tbar[:, None]

    # ax.plot(*project_to_triangle(points).T)
    triangle_points = np.array([[0,0], [np.cos(np.pi/3),np.sin(np.pi/3)], [1,0]])

    format_args = {'linestyle': 'solid', 'edgecolor': 'k'}

    plt.rcParams['hatch.linewidth'] = 0.5
    triangle = Polygon(triangle_points, closed=True, 
        facecolor = 'white', linestyle='-')
    ax.add_artist(triangle)

    chiral_phase = Polygon(project_to_triangle(points),
        closed=True, facecolor = chiral_phase_color, **format_args)#, hatch = r"////")
    ax.add_artist(chiral_phase)
    ax.scatter(*project_to_triangle(points[::4]).T, c ='k', s = 3)

    ax.axis('off')

    # ax.text(*triangle_points[0], "$J_x$", va = "top", ha = "right")
    # ax.text(*triangle_points[1] + [0,0.01], "$J_y$", va = "bottom", ha = "center")
    # ax.text(*triangle_points[2], "$J_z$", va = "top", ha = "left")
    
    center = project_to_triangle(np.array([[1,1,1],])/3)[0]
    ax.text(*center, "$B$", va = "center", ha = "center")
    corners = project_to_triangle(np.array([[1,0,0], [0,1,0], [0,0,1]]))
    t = 0.6
    for c, l in zip(corners, 'xyz'):
        ax.text(*((1-t)*center + t*c), f"$A_{l}$", va = "center", ha = "center")


plot_phase_diagram(axes[2])

fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')

