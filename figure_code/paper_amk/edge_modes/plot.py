import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import koala.plotting as pl

from cutting_utils import *

column_width = 3.375

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})

# load data

data = np.load('big_lattice_ground_state.npy', allow_pickle=True).tolist()
lattice, coloring = np.load('big_lattice.pickle', allow_pickle=True).values()
lattice = cut_patch(lattice, factor = 0.9)

vectors = data['vectors']

# plot edge modes

idx_to_plot = 2

fig, axes = plt.subplots()
fig.set_size_inches(1.3*column_width, column_width)

# pl.plot_edges(lattice, alpha=0.1, color_scheme=['w'])
xv,yv,s = pl.plot_scalar(lattice, np.abs(vectors[:,idx_to_plot]), cmap = 'inferno', vmin=None, vmax = 0.05, resolution=200)
# plot_scalar doesn't return the mappable so I'm just
# double plotting here to get the mappable for colorbar
im = axes.pcolormesh(xv,yv,s,cmap='inferno',vmin=0.0,vmax=0.05)

# tweaks + formatting

axes.set_xticks([])
axes.set_yticks([])
axes.axis('off')

cbar = plt.colorbar(im, ax=axes)
cbar.set_label(r"$|\psi|$")

plt.tight_layout()
plt.savefig('edge_modes.pdf')
