#!/usr/bin/env python3
import matplotlib
from matplotlib.colors import to_rgba, to_hex
from matplotlib import cm
from matplotlib.patches import Polygon

import matplotlib.pyplot as plt
import numpy as np
import pickle
from pathlib import Path

from koala import phase_diagrams as pd
from koala import plotting as pl

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

chiral_phase_color = matplotlib.colors.to_hex(matplotlib.cm.inferno(0.75))
line_colors = [matplotlib.colors.to_hex(a) for a in matplotlib.cm.inferno([0.25, 0.5, 0.75])]

from matplotlib.colors import LinearSegmentedColormap

diverging = LinearSegmentedColormap.from_list('divergin_orange_purple', (
                 (0.0, line_colors[0]),
                 (0.5, (1, 1, 1, 1)),
                 (1.0, line_colors[2])))

oranges = LinearSegmentedColormap.from_list('oranges', (
                (0.0, (1, 1, 1, 1)),
                (1.0, line_colors[2]),
                ))

def plot_index(lattice, index, ax):
    norm = matplotlib.colors.TwoSlopeNorm(vcenter = 0)
    im = ax.tripcolor(*lattice.vertices.positions.T, index, norm = norm, cmap = diverging)
    return im 

with open("chern_number_phase_diagram.pickle", "rb") as f:
    data = pickle.load(f)

ncols = 3
fig, all_axes = plt.subplots(2,3, figsize = (2 * w, 2/2.5 * w),
                        gridspec_kw = dict(
                            height_ratios = (1,0.1),
                            hspace = 0.1,
                            )
                        )

axes = all_axes[0]
not_used, colorbar_ax, chern_colorbar_ax  = all_axes[1]
not_used.axis('off')

radius, lattice, coloring, crosshair_position, crosshair_marker, chern_marker = data['plot1'].values()
ax = axes[1]
cb = plot_index(lattice, crosshair_marker, ax)


pl.plot_edges(lattice, alpha = 0.2, ax = ax, linewidth = 0.5)
ax.axvline(x = 0.5, linestyle = 'dotted', color = 'k', linewidth = 1)
ax.axhline(y = 0.5, linestyle = 'dotted', color = 'k', linewidth = 1)
ax.add_artist(matplotlib.patches.Circle([.5,.5], 
                radius=radius, facecolor = 'none', 
                edgecolor = 'k', linestyle = 'dotted',
                linewidth = 1))

ax.set(xticks = [], yticks = [])

plt.colorbar(mappable = cb, cax = colorbar_ax, orientation = 'horizontal')
colorbar_ax.set(xticks = [-0.03, 0, 0.05])
# colorbar_ax.axvline(x = 0, linestyle = 'dotted', color = 'k')
colorbar_ax.set(xlabel = "Crosshair Marker")

radii, J_non_abelian, non_abelian, J_abelian, abelian = data['plot2'].values()
ax = axes[0]
ax.plot(radii, non_abelian, color = line_colors[1], label = "nA")
ax.plot(radii, abelian, color = line_colors[2], label = "A")
ax.set(ylabel = "Crosshair Marker Sum", xlabel = "Sum Radius (r)")
ax.axvline(x = radius, linestyle = 'dotted', color = 'k')
# ax.legend()

symmetric, sampling_points, crosshair_phase_diagram = data['plot3'].values()
samples = 30
ax = axes[2]

if symmetric: sampling_points, triangulation = pd.get_triangular_sampling_points(samples = samples)
else: sampling_points, triangulation = pd.get_non_symmetric_triangular_sampling_points(samples = samples)

if symmetric: cb2 = pd.plot_tri(ax, crosshair_phase_diagram, triangulation, cmap = oranges, vmin = 0.07, vmax = 1)
else: cb2 = ax.tricontourf(triangulation, crosshair_phase_diagram, cmap = oranges)

plt.colorbar(mappable = cb2, cax = chern_colorbar_ax, orientation = 'horizontal')
chern_colorbar_ax.set(xticks = [0., 0.5, 1.0], xlim = [0,1])
# chern_colorbar_ax.axvline(x = 0, linestyle = 'dotted', color = 'k')
chern_colorbar_ax.set(xlabel = "Crosshair Marker Sum")

pd.plot_triangle(ax)
ax.set(xlim = (-0.01,1), ylim = (-0.01,1),)
ax.axis('off')

# fig.tight_layout()
fig.subplots_adjust(bottom = .2)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)

