#!/usr/bin/env python3
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
fontweight='bold'

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


def TJ_phase_diagram_T(ax):
    with open(data_location / 'TJ_phase_data.pickle', 'rb') as file: 
        TJ_data = pickle.load(file)   
        
    
    with open(data_location / 'TJ_phase_cdw_line.pickle', 'rb') as file: 
        crit_line = Munch(pickle.load(file))

    crit_fit_line = Munch(Ts = crit_line.fit.a*TJ_data.Js + crit_line.fit.b, Js = TJ_data.Js)
    crit_fit_line =  Munch(Ts = np.insert(crit_line.Ts, 1, 0), Js = np.insert(crit_line.Js, 1, 0))
    
    
    ax.fill_betweenx(crit_fit_line.Js, x1 = 0, x2 = crit_fit_line.Ts, color = cdw_color)
    ax.fill_between(crit_fit_line.Ts, crit_fit_line.Js, color = gapped_color)
    ax.plot(crit_fit_line.Ts, crit_fit_line.Js,  color = 'black', marker = None, markersize = 0, linewidth = 1, linestyle = 'solid')
    
    ax.plot(crit_line.Ts, crit_line.Js,  color = 'black', marker = '.', markersize = 2, linewidth = 0)
    ax.errorbar(crit_line.Ts, crit_line.Js, xerr = crit_line.dTs, color = 'k', linewidth = 0.5, capsize = 1, linestyle = '')
        
    
    #pcol.set_edgecolor('face')
    ax.set(xlim = (0.1, 5), ylim = (0,10))
    ax.set_ylabel('J', rotation=0, labelpad=10)
    ax.set_xlabel('T', rotation=0, labelpad=5)
    
    ax.text(0.15, 0.8, "CDW", transform=ax.transAxes,
            fontsize=12, fontweight=fontweight, va='top')

    ax.text(0.6, 0.35, "Mott", transform=ax.transAxes,
            fontsize=12, fontweight=fontweight, va='top')

def TU_phase_diagram_T(ax):
    with open( data_location / 'TU_phase_data.pickle', 'rb') as file: 
        TU_data = pickle.load(file)   
        
    with open(data_location / 'TU_phase_gap_gapless_line.pickle', 'rb') as file: 
        gapped_gapless_line = Munch(pickle.load(file))
    
    with open(data_location / 'TU_phase_cdw_line.pickle', 'rb') as file: 
        cdw_line = Munch(pickle.load(file))
    
    
    from matplotlib.colors import LinearSegmentedColormap
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    colors = [(1,1,1,1), cdw_color]
    cmap = LinearSegmentedColormap.from_list("mycmap", colors)

    #### Critical Lines ################
    try:
        ix = gapped_gapless_line.T > p.Tc
        
        #tack on an extra point to the gap-gappless critical line to make it meet the cdw line
        gapped_gapless_line.U = np.concatenate([[gapped_gapless_line.U[ix][0]], gapped_gapless_line.U[ix]])[::2]
        gapped_gapless_line.T = np.concatenate([[p.Tc,], gapped_gapless_line.T[ix]])[::2]
        gapped_gapless_line.dU = np.concatenate([[gapped_gapless_line.dU[ix][0]], gapped_gapless_line.dU[ix]])[::2]
    
        ax.plot(gapped_gapless_line.T, gapped_gapless_line.U, color = 'black', marker = '.', markersize = 2, linewidth = 1)
        ax.errorbar(gapped_gapless_line.T, gapped_gapless_line.U, yerr = gapped_gapless_line.dU, color = 'k', linestyle = '')
        
        ax.plot(cdw_line.T, cdw_line.U,  color = 'black', marker = '.', markersize = 2, linewidth = 1)
        ax.errorbar(cdw_line.T, cdw_line.U, xerr = cdw_line.dT, color = 'k', linestyle = '', capsize = 1, linewidth = 1)
        
        #make a polygon for the gapped region starting from top right corner
        #               top right                   left edge                             bottom edge           bottom right
        T = np.concatenate([[5,], cdw_line.T[cdw_line.U > gapped_gapless_line.U[0]][::-1], gapped_gapless_line.T, [5,]])
        U = np.concatenate([[8,], cdw_line.U[cdw_line.U > gapped_gapless_line.U[0]][::-1], gapped_gapless_line.U, [4,]])
        xy = np.array([T,U]).T
        poly = mpl.patches.Polygon(xy, closed=True, fill=True, facecolor = gapped_color, edgecolor = None)
        ax.add_artist(poly)
        
        #make a polygon for the gappless region starting from top left
        #               
        T = np.concatenate([cdw_line.T[cdw_line.U < gapped_gapless_line.U[0]][::-1], [5,5], gapped_gapless_line.T[::-1]])
        U = np.concatenate([cdw_line.U[cdw_line.U < gapped_gapless_line.U[0]][::-1], [0,4], gapped_gapless_line.U[::-1]])
        xy = np.array([T,U]).T
        poly = mpl.patches.Polygon(xy, closed=True, fill=True, facecolor = gapless_color, edgecolor = None)
        ax.add_artist(poly)
        
        #make a polygon for the cdw region starting from top left
        #               
        T = np.concatenate([[0,0], cdw_line.T])
        U = np.concatenate([[8,0],cdw_line.U])
        xy = np.array([T,U]).T
        poly = mpl.patches.Polygon(xy, closed=True, fill=True, facecolor = cdw_color, edgecolor = None)
        ax.add_artist(poly)
        
        
    except AssertionError:
        pass

    ##### labels and limits ##########################
    ax.set_ylabel('U', rotation=0, labelpad=10)
    ax.set_xlabel('T', rotation=0, labelpad=5)
    
    ax.set(ylim = (0,8), xlim = (0.1,5))

    ##### U = 0 line ##########################
    ax.hlines([0,],xmin = 0, xmax = 5,
                   linewidth = 4, color = 'black', 
                   linestyle = 'solid',
                   alpha = 0,
                   )

    ##### Text ##########################
#     x = 0.1; y = 0.2
#     ax.text(x, y, "FG", transform=ax.transData,
#         fontsize=7, fontweight=fontweight, va='bottom', ha = 'left')
    
#     ax.arrow(x+0.7, y+0.6, dx = 0, dy = -0.53,
#         width = 0.06, linewidth = 0.005, color = 'k',
#         transform=ax.transData,
#         zorder = 100,
#         )

    ax.text(1, 4, "CDW", transform=ax.transData,
            fontsize=12, fontweight=fontweight, va='center', ha = 'center')

    ax.text((Tc+5)/2, 6, "Mott", transform=ax.transData,
            fontsize=12, fontweight=fontweight, va='center', ha = 'center')
    
    ax.text((Tc+5)/2, 2, "Anderson", transform=ax.transData,
        fontsize=12, fontweight=fontweight, va='center', ha = 'center')

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

TJax = axes[0]
TUax = axes[1]

TJ_phase_diagram_T(TJax)
TU_phase_diagram_T(TUax)

# ## the triangular critical point marker
m = Munch(marker = '^', markersize = 2, color = 'black')
TJax.plot([p.Tc,], [p.J,], **m)
TUax.plot([p.Tc,], [p.U,], **m)

axes[1].yaxis.tick_right()
axes[1].yaxis.set_label_position("right")


TJax.hlines(y = 5, xmin = 0, xmax = 5, linestyle = 'dashed', linewidth = 0.7, color = 'k')
TUax.hlines(y = 5, xmin = 0, xmax = 5, linestyle = 'dashed', linewidth = 0.7, color = 'k')

TJax.set_box_aspect(1)
TUax.set_box_aspect(1)

#the TJ plot
TJax.set(xlim = (0,4),
            xticks = [0,1,2,3,4],
            yticks = [0, 2, 4, 6, 8],
            ylim = (0,8),
            )

TUax.set(xlim = (0,5),
            xticks = [0,1,2,3,4,5],
            yticks = [0, 2, 4, 6, 8],
            ylim = (0,8),
            )

fig.tight_layout()

fig.savefig(f'./{Path.cwd().name}.pdf')
fig.savefig(f'./{Path.cwd().name}.svg', transparent = False)


    


# m2ax = axes[0]
# binderax = axes[1]


# binder(binderax)
# orderparam(m2ax)

# ## the triangular critical point marker
# m = Munch(marker = '^', markersize = 2, color = 'black')
# binderax.plot([p.Tc,], [p.B,], **m)
# m2ax.plot([p.Tc,], [p.m2,], **m)
# TJax.plot([p.Tc,], [p.J,], **m)
# TUax.plot([p.Tc,], [p.U,], **m)

# #### the M2 plot #####

# #The m2 plot
# m2ax.set(xlim = (0,4),
#             xticks = [0,1,2,3],
#             yticks = [0, 0.5, 1],
#             yticklabels = ['0', '.5', '1']
#             )

# # startx = 1.6; starty = 0.19;
# # endx = 2; endy = 0.2;
# # m2ax.arrow(startx, starty, endx-startx, endy-starty, width = 0.01, linewidth = 0.001, color = 'k')
# # m2ax.text(startx-0.05, starty, 'N = 250', fontsize = 7, ha = 'right', va = 'center')

# # startx = 2.5; starty = 0.57;
# # endx = 2.15; endy = 0.56;
# # m2ax.arrow(startx, starty, endx-startx, endy-starty, width = 0.01, linewidth = 0.001, color = 'k')
# # m2ax.text(startx+0.05, starty, 'N = 10', fontsize = 7, ha = 'left', va = 'center')


# ######## Things that depend on where the axis is rather than what is on it
# axes[0].xaxis.tick_top()
# axes[0].xaxis.set_label_position("top")

# axes[1].yaxis.tick_right()
# axes[1].yaxis.set_label_position("right")

# axes[1].xaxis.tick_top()
# axes[1].xaxis.set_label_position("top")
    
# axes[3].yaxis.tick_right()
# axes[3].yaxis.set_label_position("right")

  
# for letter, ax, c in zip('abcdef...', axes.flatten(), 'kkkk'):
#     ax.text(0.03, 0.92, f"({letter})", transform=ax.transAxes,
#             fontsize=7, fontweight=fontweight, va='top', color = c)



# TJax.hlines(y = 5, xmin = 0, xmax = 5, linestyle = 'dashed', linewidth = 0.7, color = 'k')
# TUax.hlines(y = 5, xmin = 0, xmax = 5, linestyle = 'dashed', linewidth = 0.7, color = 'k')

# #the binder plot
# binderax.set(xticks = [1.5, 2, 2.5],
#             xticklabels = ['1.5', '2', '2.5'],
#            )

# #the TJ plot
# TJax.set(xlim = (0,4),
#             xticks = [0,1,2,3],
#             yticks = [0, 2, 4, 6, 8],
#             ylim = (0,8),
#             )

# TUax.set(xlim = (0,5),
#             xticks = [0,1,2,3,4],
#             yticks = [0, 2, 4, 6, 8],
#             ylim = (0,8),
#             )

# #work in figure coords where (0,0) is bottom left and (1,1) top right
# (_, _), (_, y0) = binderax.get_position().get_points()
# (_, y1), (_, _) = TUax.get_position().get_points()
# y2 = y1 + 0.02

# dont_care = 0

# def datacoords_to_fig(ax, point): 
#     trans = ax.transData + f.transFigure.inverted()
#     return trans.transform_point(point) #transform to figure coords

# import matplotlib.lines as lines

# lineargs = dict(
#     linewidth=0.8, linestyle=None, color='k', transform = f.transFigure,
# )

# for xval in binderax.get_xlim():
#     (x0, _) = datacoords_to_fig(binderax, (xval, dont_care))
#     (x1, _) = datacoords_to_fig(TUax, (xval, dont_care))
#     f.add_artist(lines.Line2D([x0, x1], [y0, y1], **lineargs,))
#     f.add_artist(lines.Line2D([x1, x1], [y1, y2], **lineargs,))
    
# f.set_size_inches(columnwidth, columnwidth)
# f.savefig(figure_location / 'phase_diagram.eps', bbox_inches='tight')
# f.savefig(figure_location / 'phase_diagram.svg', bbox_inches='tight')
