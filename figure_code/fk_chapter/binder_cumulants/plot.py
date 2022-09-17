#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pickle
from munch import Munch
import matplotlib as mpl

from FKMC.general import smooth
import matplotlib.gridspec as gridspec
from itertools import count

column_width = w = 3.375
black_line_widths = 1.2

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.expanduser('~/git/Thesis/figure_code')))
from plot_settings import bond_colors, line_colors, plaq_color_scheme

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.expanduser('~/FKMC/notebooks/short_paper_figure_code')))
from customcolors import colors, colors10, custom_cmap

np.seterr(under = 'ignore')

data_location = Path('~/HPC_data/pickled_data').expanduser()
figure_location = Path('~/git/FK_short_paper/figs').expanduser()

rng = np.random.default_rng(222424252565)

from matplotlib.colors import to_rgba

cdw_color = to_rgba('#f09000')
gapped_color = to_rgba('#00afdb')
gapless_color = to_rgba('#e1a3f0')

#Sohpie's colour scheme
gapped_color = colors[3]
gapless_color = colors[-1]
cdw_gapped_midpoint = np.mean([cdw_color, gapped_color], axis = 0)

Tc = 2.25

from scipy.interpolate import interp1d, UnivariateSpline

def binder(ax):
    with open(data_location / 'binder_data.pickle', 'rb') as file: 
        d = oBinder = Munch(pickle.load(file))
    
    for i, N, c in zip(count(), d.Ns, colors):
        d.dB[i] = np.maximum(d.dB[i], d.dB[i].mean() * 0.1)
        binder_interped = UnivariateSpline(d.BX, d.B[i], w = 1/d.dB[i], s = len(d.BX))
        x = np.linspace(d.BX[0], d.BX[-1], 200)
        ax.plot(x, binder_interped(x), color = c)
        
    ax.set_ylabel('B', rotation=0, labelpad=5)
    ax.set_xlabel('T', rotation=0, labelpad=5)
        
        
def orderparam(ax):
    with open(data_location / 'binder_data.pickle', 'rb') as file: 
        d = oBinder = Munch(pickle.load(file))
    
    with open(data_location / 'fermion_binder_data.pickle', 'rb') as file: 
        fermion = Munch(pickle.load(file))
    
    for i, N, c in zip(count(), d.Ns, colors):
        d.dM2[i] = np.maximum(d.dM2[i], d.dM2[i].mean() * 0.1)
        M_interped = UnivariateSpline(d.MX, d.M2[i], w = 1/(d.dM2[i] + 0.01*max(d.dM2[i])), s = len(d.MX))
        #axes[0].plot(d.MX, d.M2[i], linewidth = 1, color = c)
        #axes[0].errorbar(d.MX, d.M2[i], yerr = d.dM2[i] * 2, color = c, linestyle = "None", marker = '|', markersize = 0.5, label = f'N = {N}')

        x = np.linspace(d.MX[0], d.MX[-1], 200)
        ax.plot(x, M_interped(x), color = c)
        
        fermion.do[i] = np.maximum(fermion.do[i], fermion.do[i].mean() * 0.1)
        o_interped = UnivariateSpline(d.MX, fermion.o[i], w = 1/fermion.do[i], s = len(d.MX))
        ax.plot(x, 1 - o_interped(x), color = c,linestyle = '--')
        #spread(axes[0], d.MX, d.M2[i], d.dM2[i], alpha = 0.3, label = f'N = {N}', color = color)
        
#         ax.set_ylabel('$m^2$', rotation=0, labelpad=7)
        ax.set_xlabel('T', rotation=0, labelpad=5)

#the point at the binder crossing
p = Munch(J = 5, U = 5)

with open(data_location / 'TJ_phase_cdw_line.pickle', 'rb') as file: 
    crit_line = Munch(pickle.load(file))
p.Tc = crit_line.fit.a*5 + crit_line.fit.b

with open(data_location / 'binder_data.pickle', 'rb') as file: 
    d = oBinder = Munch(pickle.load(file))
p.B = np.interp(p.Tc, d.BX, d.B[-1]) 
p.m2 = np.interp(p.Tc, d.MX, d.M2[-1])


fig, axes = plt.subplots(1, 2, figsize = (4/3 * w, 2/3 * w))

m2ax = axes[0]
binderax = axes[1]

binder(binderax)
orderparam(m2ax)

axes[1].yaxis.tick_right()
axes[1].yaxis.set_label_position("right")

# ## the triangular critical point marker
m = Munch(marker = '^', markersize = 2, color = 'black')
binderax.plot([p.Tc,], [p.B,], **m)
m2ax.plot([p.Tc,], [p.m2,], **m)

#The m2 plot
m2ax.set(xlim = (0,4),
            xticks = [0,1,2,3],
            yticks = [0, 0.5, 1],
            yticklabels = ['0', '.5', '1']
            )

# startx = 1.6; starty = 0.19;
# endx = 2; endy = 0.2;
# m2ax.arrow(startx, starty, endx-startx, endy-starty, width = 0.01, linewidth = 0.001, color = 'k')
# m2ax.text(startx-0.05, starty, 'N = 250', fontsize = 7, ha = 'right', va = 'center')

# startx = 2.5; starty = 0.57;
# endx = 2.15; endy = 0.56;
# m2ax.arrow(startx, starty, endx-startx, endy-starty, width = 0.01, linewidth = 0.001, color = 'k')
# m2ax.text(startx+0.05, starty, 'N = 10', fontsize = 7, ha = 'left', va = 'center')


#the binder plot
binderax.set(xticks = [1.5, 2, 2.5],
            xticklabels = ['1.5', '2', '2.5'],
           )

m2ax.set_box_aspect(1)
binderax.set_box_aspect(1)


fig.tight_layout()

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg', transparent = False)

