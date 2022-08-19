#!/usr/bin/env python3
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from koala import phase_diagrams as pd


def line(start, end, npoints):
    t = np.linspace(0,1,npoints)[:, None]
    return start * (1-t) + end * t

symmetry_points = np.array([[0,0.5,0.5], [0.5,0,0.5], [0.5,0.5,0]])
center = np.array([1,1,1])/3
lines = []

triplets = np.array([
    [
    [0,0,1], #z
    [0, 0.5, 0.5],
    [0.5, 0, 0.5]
    ],
    [
    [0,1,0], #y
    [0.5, 0.5, 0],
    [0, 0.5, 0.5]
    ],
    [
    [1,0,0], #x
    [0.5, 0, 0.5],
    [0.5, 0.5, 0]
    ]
])

## User Parameters ### 
n_lines = 4

## End of user parameters

t = np.linspace(0,1,n_lines)[:, None]

logo_lines = []
for corner, left, right in triplets:
    line_ends = left * t + (1-t) * center
    line_ends2 = center * t + right * (1-t)
    line_ends = np.concatenate([line_ends2[:-1], line_ends])

    for e in line_ends:
        logo_lines.append([corner, e])
        
lines = np.array(logo_lines)

# imports just for this plot

column_width = w = 3.375
black_line_widths = 1.2
matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})


def project_to_triangle(points): 
    skew = np.array([[1, np.cos(np.pi/3)],
                          [0, np.sin(np.pi/3)]])

    return np.einsum('ij,kj -> ki', skew, points[..., :2])

fig, ax = plt.subplots(nrows=1, ncols=1)
fig.set_size_inches(w, w)
ax.axis('off')

for i, (s, e) in enumerate(lines):
    p = line(s, e, npoints = 20)
    ax.plot(*project_to_triangle(p).T, color = 'k')
    
pd.plot_triangle(ax)
triangle_points = np.array([[0,0], [np.cos(np.pi/3),np.sin(np.pi/3)], [1,0]])
# ax.text(*triangle_points[0], "$J_x$", va = "top", ha = "right")
# ax.text(*triangle_points[1] + [0,0.01], "$J_y$", va = "bottom", ha = "center")
# ax.text(*triangle_points[2], "$J_z$", va = "top", ha = "left")

# fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)

