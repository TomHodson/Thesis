#!/usr/bin/env python3

import matplotlib
from matplotlib.colors import to_rgba, to_hex
from matplotlib import cm

import matplotlib.pyplot as plt
import numpy as np
import pickle
from pathlib import Path



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

ncols = 1
fig, ax = plt.subplots(nrows=1, ncols=ncols)
fig.set_size_inches(2 * w, w)

with open("lattice_generation_times.pickle", 'rb') as f:
    periods, ts, Ls = pickle.load(f).values()

bottom = np.zeros(shape = ts.shape[1])
for stack, label in zip(ts[::-1], periods[::-1]):
    ax.bar(Ls, stack, width = np.concatenate([[Ls[0]], np.diff(Ls)]), label=label, bottom = bottom)
    bottom += stack
    
ax.legend()
ax.set(ylabel = "Time (s)", xlabel = "Number of Plaquettes")



fig.tight_layout()
# fig.subplots_adjust(left = 0.01, wspace=.05, right = 1 - 0.01, top = 1 - 0.01, bottom = 0.01)

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg')

