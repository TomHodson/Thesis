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
import scipy

column_width = w = 3.375
black_line_widths = 1.2
fontweight='bold'
text_fontsize=12

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

#Sophie's colour scheme
gapped_color = colors[3]
gapless_color = colors[-1]
cdw_gapped_midpoint = np.mean([cdw_color, gapped_color], axis = 0)

###################################################################
DOSxlim = np.array([0, 1.2])
DOSylim = (-0.1,1.5)

IPRylim = (0.03, 0.3)
Es = [
    lambda o: 1/16 * 0.9 if o.parameters.U == 2 else 1/4 * 0.96,
    lambda o: 1/4 * (1 + np.sqrt(1 + 16/o.parameters.U**2)),
     ]

linewidth = 0.5
legend_fontsize=9.5
legend_wspace = 0.01
legend_labelspacing = 0.3
legend_axis_rel_width = 0.4
wspace = 0
hspace = 0

with open(Path('~/HPC_data/pickled_data/individual_IPRs.pickle').expanduser(), 'rb') as file:
    os = pickle.load(file)

from FKMC.general import get_nearby_index

def pulloutbytemp_and_U(o, T_i, U_i):
    newo = o.copy()
    newo.DOS = newo.DOS[:, U_i, T_i]
    newo.IPR = newo.IPR[:, U_i, T_i]
    newo.dDOS = newo.dDOS[:, U_i, T_i]
    newo.dIPR = newo.dIPR[:, U_i, T_i]
    newo.Mf_moments = newo.Mf_moments[:, :, U_i, T_i, :]
    newo.parameters.beta = 1 / o.Ts[T_i]
    newo.parameters.U = o.Us[U_i]
    return newo


def plot_DOS(ax, o, letter):
    DOS = np.where(o.DOS > 0.001, o.DOS, np.NaN)
    lines = [None for _ in o.Ns]
    for i, N in list(enumerate(o.Ns))[::-1]:
        lines[i], = ax.plot(o.E_bins[1:] / o.parameters.U, DOS[i], label = f'N = {N}', color = colors10[i], linewidth = linewidth) 
        
    xlim = 1/2 * np.sqrt(1 + 16/o.parameters.U**2) * DOSxlim
    ax.set(xlim = xlim, ylim = DOSylim)
    
    #do the arrows showing where the IPRs are taken
    for e in Es: 
        true_E, E_i = get_nearby_index(o.E_bins[1:] / o.parameters.U, e(o))
        x, y = (true_E, max(o.DOS[:, E_i]))
        ax.vlines(x, ax.get_ylim()[0], ax.get_ylim()[1], colors='k', linestyles='dotted', linewidth = linewidth)

    label = "\n".join([
             f"({letter})",
             f"T = {1 / o.parameters.beta}",
             f"U = {o.parameters.U}",
             ])
    ax.text(0.06, 0.96, label, transform=ax.transAxes,
            fontsize=text_fontsize, fontweight=fontweight, va='top', color = 'black')
    
    return lines

disorder_taus = {'a':[0,0], 'b':[0,0], 'c':[0,0], 'd':[0,0],}
def plot_IPR_scaling(ax, o, letter):
    lines = [None for _ in Es]
    print(f'\nU = {o.parameters.U} T = {1/o.parameters.beta}')
    print(f'm^2 = {list(o.Mf_moments[:, :, 2].mean(axis = 1))}')
    for i, e, linestyle in zip(count(), Es, ['dashed', 'dotted']): 
        true_E, E_i = get_nearby_index(o.E_bins[1:] / o.parameters.U, e(o))
        print(f'\omega_{i} = {true_E:.3f}')
        IvN = np.array([o.IPR[i, E_i] for i, _ in enumerate(o.Ns)])
        dIvN = np.array([o.dIPR[i, E_i] for i, _ in enumerate(o.Ns)])

        #model is IPR(N) = A * N ^ (-tau)
        def IPR(N, A, tau): return A * N ** (-tau)
        idx = o.Ns > 70
        (A, tau), pcov = scipy.optimize.curve_fit(IPR, o.Ns[idx], IvN[idx], p0=(0.5, 0.5), sigma=dIvN[idx], absolute_sigma=True)
        dA, dtau = np.sqrt(np.diag(pcov))
        
        lines[i], = ax.plot(o.Ns, IPR(o.Ns, A, tau), linestyle = linestyle, color = 'k', marker = None, linewidth = linewidth*2)
        #ax.errorbar(o.Ns, IvN, yerr = dIvN, fmt = 'none', ecolor = 'k',
        #            elinewidth = linewidth / 2, capsize = 1, capthick = linewidth / 2)
        ax.scatter(o.Ns, IvN, c = colors10, s = 2, zorder = 3)
        
        def errorfmt(a, da):
            digit = -int(np.floor(np.log10(da)))
            d = f'{da:.1g}'[-1]
            return f'{a:.{digit}f}({d})'
        
        disorder_taus[letter][i] = f"{tau:.2f}\pm{dtau:.2f}"
        print(f'\\tau_{i} = {tau:.2f}\pm{dtau:.2f}')
        
        
        ax.set(
               yscale = 'log', 
               xscale = 'log',
               ylim = IPRylim,
              )
        
    label = " ".join([
             f"({letter})",
             f"T = {1 / o.parameters.beta}",
             f"U = {o.parameters.U}",
             ])
    ax.text(0.02, 0.9, label, transform=ax.transAxes,
            fontsize=text_fontsize, fontweight=fontweight, va='top', color = 'black')
    return lines

figs = [plt.figure(constrained_layout=False), plt.figure(constrained_layout=False)]

#make a split between the top and bottom
# gs = f.add_gridspec(ncols = 1, nrows = 2, hspace = 0.2)
groups = [None, None]
legend_axes = [None, None]

for i, f in enumerate(figs):
    sgs = f.add_gridspec(nrows = 2, ncols = 3, 
                                      width_ratios=[1, 1, legend_axis_rel_width],
                                      hspace = 0,
                                      wspace = 0,
                                      bottom =  0.2,
                                      top = 1-0.2,
                                     )
    groups[i] = np.array([
                 [f.add_subplot(sgs[0, 0]), f.add_subplot(sgs[1, 0])],
                 [f.add_subplot(sgs[0, 1]), f.add_subplot(sgs[1, 1])],
                ])
           
    legend_axes[i] = f.add_subplot(sgs[:, 2], visible = False)


for U_i, col, labels in zip(count(), groups[0], [['a','c'], ['b','d']]):
    for T_i, ax, label in zip([1,0], col, labels):
        o = pulloutbytemp_and_U(os, T_i = T_i, U_i = U_i)
        lines = plot_DOS(ax, o, label)
        
        ax.set(xticks = [0, 0.5] + [e(o) for e in Es],)
        
        if T_i == 1: #set the omega labels for the top of the DOS plot
            ax.tick_params(bottom = False, labelbottom = False, top = True, labeltop = True)
            ax.set(xticklabels = ['', ''] + [f'$\omega_{i}$' for i, _ in enumerate(Es)],
                  xlabel = '$\omega / U$',
                  )
            ax.xaxis.set_label_position('top')
            
        if T_i == 0: #set the numerical xlabels for the bottom of the DOS plot
            ax.tick_params(top = True, labeltop = False, labelbottom = True)
            ax.set(
            xticklabels = ['0', '.5'] + ['', ''],
            xlabel = '$\omega / U$',
            )
            
        if U_i == 0: ax.set(ylabel = 'DOS($\omega$)')
            
        phase = 'CDW' if T_i == 0 else ('Anderson' if U_i == 0 else 'Mott')
        ax.text(0.97, 0.97, phase, transform=ax.transAxes,
            fontsize=text_fontsize, fontweight=fontweight, va='top', ha='right', color = 'black')
        
        

for U_i, col, labels in zip(count(), groups[1], [['a','c'], ['b','d']]):
    for T_i, ax, label in zip([1,0], col, labels):
        phase = 'CDW' if T_i == 0 else ('Anderson' if U_i == 0 else 'Mott')
        print(f"\n{phase} Phase")
        o = pulloutbytemp_and_U(os, T_i = T_i, U_i = U_i)
        omega_lines = plot_IPR_scaling(ax, o, label)
        
        ax.set(yticks = [0.1, 1])
        
        if U_i == 0: ax.set(ylabel = 'IPR($\omega$)')
        if T_i == 0: ax.set(xlabel = 'N')
        if T_i == 1: 
            ax.tick_params(bottom = False, labelbottom = False)
            
        from matplotlib.ticker import StrMethodFormatter, NullFormatter, FixedFormatter, FixedLocator
        ax.yaxis.set_major_locator(FixedLocator([0.1, 1]))
        ax.yaxis.set_major_formatter(FixedFormatter(['.1', '1']) if U_i == 0 else NullFormatter())
        #ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.1f}') if U_i == 0 else NullFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())
        
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
        #ax.xaxis.set_minor_formatter(StrMethodFormatter('{x:.0f}'))
        
        import matplotlib.ticker as ticker
        ax.xaxis.set_minor_formatter(ticker.FuncFormatter(
            lambda x,pos: f"{x:.0f}" if x in [40.0, 60.0, 200.0] else ''
        ))

        ax.text(0.97, 0.90, phase, transform=ax.transAxes,
            fontsize=text_fontsize, fontweight=fontweight, va='top', ha='right', color = 'black')

#turn off the yticks labels for the right column
for g in groups: 
    for a in g[1, :]:
        a.tick_params(axis = 'y', labelleft = False, left=False)
        
#turn off the x ticks labels for the upper rows:
for g in groups: 
    for a in g[:, 0]:
        a.tick_params(axis = 'x', labelbottom = False)

    
def add_side_legend(f, axes, legend_axis, lines, labels, loc = 'center', rect_redefine = None):
    from matplotlib.legend import Legend
    #get the x position of the right of the plots in figure coords
    _, (x0, _) = axes[1,0].get_position().get_points()
    #get the y position of the bottom of the plots in figure coords
    (_, y0), _ = axes[1,1].get_position().get_points()
    #get the top right of the legend axis
    _, (x1, y1) = legend_axis.get_position().get_points()
    
    if rect_redefine: x0, y0, x1, y1 = rect_redefine(x0, y0, x1, y1)

    rect = mpl.patches.Rectangle((x0+legend_wspace,y0),x1-x0-legend_wspace,y1-y0,
                                 linewidth=0.7,
                                 edgecolor='k',
                                 facecolor='none',
                                 transform = f.transFigure)
    f.add_artist(rect)
    
    leg = f.legend(
                 handles = lines, 
                 labels = labels,
                 frameon=False,
                 fontsize = legend_fontsize,
                 loc = loc,
                 bbox_to_anchor=rect.get_bbox(),
                labelspacing = legend_labelspacing,
               fancybox = False,
               bbox_transform=f.transFigure,
    )
    #modify the frame of the legend
    frame = leg.get_frame()
    frame.set(visible = False)
    
    f.add_artist(leg);
    return leg, rect
    
leg, rect = add_side_legend(figs[0], axes = groups[0], legend_axis = legend_axes[0], lines=lines, 
                      labels = [f"{N}" for N in o.Ns])
leg.set_title("N =  ... ", prop = dict(size = legend_fontsize))

leg, rect = add_side_legend(figs[1], axes = groups[1], legend_axis = legend_axes[1], lines=omega_lines, loc = 'upper center', 
                    rect_redefine = lambda x0, y0, x1, y1: (x0, y1 - (y1-y0)*0.4, x1, y1),
                    labels = [f"$\omega_{i}$" for i,e in enumerate(Es)])


# print('To be included in the figure caption: \n\n')
# print(r"The measured \(\tau_0,\tau_1\) for each figure are: " +
#       " ".join(f"({letter}) \({tau0}, {tau1}\)" for letter,(tau0,tau1) in disorder_taus.items()))

for f, name in zip(figs, ["DOS", "IPR_scaling"]):
    # f.subplots_adjust()
    f.set_size_inches(2 * w, 2/2 * w)

    f.savefig(f'./{name}.pdf')
    f.savefig(f'./{name}.svg', transparent = False)