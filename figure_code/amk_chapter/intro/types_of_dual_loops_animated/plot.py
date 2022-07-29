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
from tqdm import tqdm
import subprocess

w = column_width = 3.375
black_line_widths = 1.5

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": black_line_widths})

def make_path_from_plaquettes(lattice, p):
    eps = [pathfinding.path_between_plaquettes(lattice, p[i], p[(i+1)%len(p)]) for i in range(len(p))]
    ps = list(it.chain.from_iterable(ep[0][:0:-1] for ep in eps))
    es = list(it.chain.from_iterable(ep[1][::-1] for ep in eps))
    
    return ps, es

line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]
rng = np.random.default_rng(242535)
lattice, colouring, ujk = eg.make_honeycomb(13)
    
subprocess.run(["mkdir", "-p", "./animation"])

total_frames = 20
for i in tqdm(range(total_frames)):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    aspect_ratio = 3
    fig.set_size_inches(2 * w, 2/aspect_ratio * w)


    edges_to_highlight = []
    plaquettes_to_highlight = []

    ### flip one edge ####
    p = [27,29]
    ps, es = pathfinding.path_between_plaquettes(lattice, *p)
    edges_to_highlight += es
    plaquettes_to_highlight += p

    #### flip a few edges to make a string ####
    p = [6,58]
    ps, es = pathfinding.path_between_plaquettes(lattice, *p)
    edges_to_highlight += es
    plaquettes_to_highlight += p

    ##### flip edges to make a loop #######
    p = [36, 64, 68, 44, 16, 12]
    ps, es = make_path_from_plaquettes(lattice, p)
    edges_to_highlight += es[:i]
    if i < len(ps): plaquettes_to_highlight += [ps[0], ps[i]]

    ##### make a boundary crossing loop #######
    p = [100, 22]
    ps, es = pathfinding.path_between_plaquettes(lattice, *p)
    es += [621,]

    edges_to_highlight += es[:i]
    if i < len(ps): plaquettes_to_highlight += [ps[0], ps[i]]

    pl.plot_edges(lattice, color = 'grey', alpha = 0.5)
    pl.plot_edges(lattice, subset = edges_to_highlight, color = 'k')
    pl.plot_dual(lattice, subset = edges_to_highlight, color_scheme = line_colors[1:], alpha = 0.7)
    pl.plot_plaquettes(lattice, subset = plaquettes_to_highlight, color_scheme = line_colors[2:], alpha = 0.5)



    ax.set(xticks = [],
        yticks = [],
        xlim = (0,1),
        ylim = (0,1/aspect_ratio))

    text_at_plaquettes = [
        [53,'(a)'],
        [60,'(b)'],
        [40,'(c)'],
        [51,'(d)'],
    ]

    for p_i, text in text_at_plaquettes:
        ax.text(*lattice.plaquettes[p_i].center, text, 
                ha = 'center', va = 'center',
            fontsize = 15, weight = 'bold',
            )

    if i == total_frames - 1: 
        fig.savefig(f'./{Path.cwd().name}.svg')
        fig.savefig(f'./{Path.cwd().name}.pdf')
    fig.savefig(f"animation/iteration_{i:03}.svg")
    plt.close(fig)

print("Making the gif...")
subprocess.run(["convert", "animation/*.svg", f'./{Path.cwd().name}.gif'])
subprocess.run(["rm", "-r", "./animation"])