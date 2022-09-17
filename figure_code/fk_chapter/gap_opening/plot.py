#!/usr/bin/env python3
from tkinter import FALSE
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pickle
from munch import Munch
import matplotlib as mpl

from FKMC.general import smooth
import matplotlib.gridspec as gridspec

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


def plot_gap_opening_log_2x1(f, o, olog = [None,None], xlim = (-3.5/2, 3.5/2)):
    shading = 'nearest'
    
    #the overall grid has rows (cax, ax0, ax1) and two columns
    gs0 = gridspec.GridSpec(nrows = 2, ncols = 2, figure=f, wspace = 0.03,
                                            bottom = 0.2,
                                            top = 1 - 0.2,
                                            hspace = 0.05,
                                            height_ratios = (1,10),
                                            width_ratios = (1,1))
    caxes = [f.add_subplot(gs0[0,0]), f.add_subplot(gs0[0,1])]

    j = 1
    #within each ax we split into axes and logaxes part with a subgridspec with hspace = 0
    lgs, rgs = [gs0[j, i].subgridspec(2,1, 
                                        height_ratios = (1,5),
                                        hspace = 0,
                                        ) for i in range(2)]
    axes = [f.add_subplot(lgs[1,0]), f.add_subplot(rgs[1,0])]
    logaxes = [f.add_subplot(lgs[0,0]), f.add_subplot(rgs[0,0])]


    print(f'o.Ns = {o.Ns}')
    i1 = 2; i2 = 0
    N1 = o.Ns[i1]; N2 = o.Ns[i2]
    print(f'N1 = {N1}, N2 = {N2}')


    E_i = 2
    E_threshold = 0.07
    E = smooth(o.DOS[E_i], scale = 0.5, axis = -1)
    E = np.where(E > 0.06, E, np.NaN)
    I = np.where(E > 0.06, -o.m, np.NaN)

    if olog:
        olog.E = smooth(olog.DOS[E_i], scale = 0.5, axis = -1)
        olog.E = np.where(olog.E > 0.06, olog.E, np.NaN)
        olog.I = np.where(olog.E > 0.06, -olog.m, np.NaN)
    
    custom_cmap.set_bad(color='white')
    
    #plot the E-T IPR diagram Diagram
    #the norm has to be fully specified (both vmin and vmax) so that the log and normal axes match
    DOSnorm = mpl.colors.Normalize(vmin = 0, vmax = 0.6)
    DOSpcol = axes[0].pcolormesh(o.E_bins[1:]/o.parameters.U, o.Ts, E, norm = DOSnorm, cmap=custom_cmap, linewidth=0, rasterized = True, shading = shading)
    if olog: logaxes[0].pcolormesh(o.E_bins[1:]/o.parameters.U, olog.Ts, olog.E, norm = DOSnorm, cmap=custom_cmap, linewidth=0, rasterized = True, shading = shading)

    axes[0].set(ylabel = 'T', ylim = (0.1, 4), xlim = (-4, 4))

    #plot the E-T IPR diagram Diagram
    Taunorm = mpl.colors.Normalize(vmin = 0, vmax = 1)
    taupcol = axes[1].pcolormesh(o.E_bins[1:]/o.parameters.U, o.Ts, I, norm = Taunorm, cmap= custom_cmap, linewidth=0, rasterized = True, shading = shading)
    if olog: logaxes[1].pcolormesh(o.E_bins[1:]/o.parameters.U, olog.Ts, olog.I, norm = Taunorm, cmap=custom_cmap, linewidth=0, rasterized = True, shading = shading)


    for a,b in zip(axes, logaxes): 
        #a.tick_params(direction = "in")
        b.tick_params(labelbottom = False)
        a.set(xlim = xlim)
        b.set(xlim = xlim)

        maxliny = 3.2

        a.set(ylim = (0.4,maxliny),
                yticks = [0,1,2,3],
                xlabel = '$\omega$/U',
        )
        b.set(yscale = 'log')
        b.set(
            ylim = (maxliny,100),
            yticks = [10,100],
            yticklabels = ['10','100'],
        )
        b.minorticks_off()
        
    # if j == 1: 
    #     for ax in axes: ax.tick_params(labelbottom = False)


    for a in [axes[-1], logaxes[-1]]:
        a.tick_params(labelleft = False, labelright = True, left = False, right = True)

    # remove code that does labelling for the thesis        
    # labels = ["(a)","(b)"] if j == 1 else ["(c)","(d)"]
    # for label, ax, color in zip(labels, axes, ['k', 'k']):
    #     ax.text(0.02, 0.03, label, transform=ax.transAxes, va='bottom', ha = 'left',
    #             fontsize=7, fontweight='normal', color = color)
    #     ax.text(0.99, 0.03, f'U={o.parameters.U}', transform=ax.transAxes, va='bottom', ha = 'right',
    #             fontsize=7, fontweight='normal', color = color)

    Tc = 2.3
    #pm 1/2 np.sqrt(4*U**2 + 8t**2(1 + cos(ka)))
    bounds = np.array([-1,-1,+1,+1]) * 0.5 * np.sqrt(o.parameters.U**2 + 8*np.array([0,2,0,2])) / o.parameters.U
    #bounds = [-2.3/2, -0.9/2, 0.9/2, 2.3/2]

    for ax in axes[:2]:
        ax.hlines(y = Tc, xmin = -4, xmax = 4, linewidth = 0.7, linestyle = 'dotted', color = 'k')
        ax.vlines(x = bounds, ymin = 0, ymax = Tc, linewidth = 0.7, linestyle = 'dotted', color = 'k')
    
    for a in axes: a.set(ylim = (0.4,maxliny))
    
    DOScbar = f.colorbar(DOSpcol, cax = caxes[0], orientation="horizontal")
    caxes[0].set(xlabel = 'DOS')  
    caxes[0].xaxis.set_label_position('top') 
    DOScbar.set_ticks([0, .25, .5])
    DOScbar.set_ticklabels(['0', '.25', '.5'])
    caxes[0].tick_params(bottom = False, top = True, labelbottom = False, labeltop = True)
    
    taucbar = f.colorbar(taupcol, cax = caxes[1], orientation="horizontal")
    caxes[1].set(xlabel = r'$\tau$')  
    caxes[1].xaxis.set_label_position('top') 
    taucbar.set_ticks([0, .5, 1])
    taucbar.set_ticklabels(['0', '.5', '1'])
    caxes[1].tick_params(bottom = False, top = True, labelbottom = False, labeltop = True)

    return f
 
with open(Path('~/HPC_data/pickled_data/gap_opening.pickle').expanduser(), 'rb') as file:
    o = pickle.load(file)
    
with open(Path('~/HPC_data/pickled_data/gap_opening_high_temp_log.pickle').expanduser(), 'rb') as file:
    olog = pickle.load(file)
    
with open(Path('~/HPC_data/pickled_data/gap_opening_U=5.pickle').expanduser(), 'rb') as file:
    oU5 = pickle.load(file)
    
with open(Path('~/HPC_data/pickled_data/gap_opening_U=5_log.pickle').expanduser(), 'rb') as file:
    oU5log = pickle.load(file)

ncols = 3
fig = plt.figure()
fig.set_size_inches(2 * w, 2/2 * w)
plot_gap_opening_log_2x1(fig, o, olog, xlim = (0,1.7))


fig.savefig(f'./{Path.cwd().name}_U2.pdf')
fig.savefig(f'./{Path.cwd().name}_U2.svg', transparent = False)

fig = plt.figure()
fig.set_size_inches(2 * w, 2/2 * w)
plot_gap_opening_log_2x1(fig, oU5, oU5log, xlim = (0,1.7))

fig.savefig(f'./{Path.cwd().name}_U5.pdf')
fig.savefig(f'./{Path.cwd().name}_U5.svg', transparent = False)
