#!/usr/bin/env python3
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pickle
from dataclasses import dataclass
from scipy.stats import sem
from matplotlib import cm
import matplotlib.gridspec as gridspec
matplotlib.rcParams['figure.dpi'] = 200

from pathlib import Path

@dataclass
class PlotData:
    name: str
    location: str
    Ls = None
    gaps = None

with open("gap_vs_L_aggregated.pickle", 'rb') as f:
    plot_data = pickle.load(f)

# %%
column_width = 3.375
matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
line_colors = [cm.inferno(X) for X in [0.25, 0.5, 0.75]]


# fig = plt.figure(figsize = (column_width,column_width))
# gs = gridspec.GridSpec(nrows = 2, ncols = 2, figure=fig, wspace = 0.05, hspace = 0.5, left = 0.2, bottom = 0.1)
# axes = [fig.add_subplot(gs[0,:]), fig.add_subplot(gs[1,:])]

fig, ax = plt.subplots(nrows=1, ncols=1)
fig.set_size_inches(2 * column_width, 2/2 * column_width)


# #### Top Plot
# ax = axes[0]
# ax.set(ylabel = "$\Delta_{\mathrm{f}}/J$", xlabel = r"Vortex Density $\rho$")
# ax.text(-0.25,1,'a)', transform = ax.transAxes)

### Bottom Plot
def scale(L): return L

for plot,color in zip(plot_data, line_colors[::2]):
    print(f"{plot.name} data contains nans indicating missing data: {~np.all(np.isfinite(plot.gaps))}")
    x = plot.Ls
    mean = np.nanmean(plot.gaps, axis = -1)
    err = sem(plot.gaps, axis = -1, nan_policy = 'omit')
    
    from scipy.optimize import curve_fit
    def func(x, a,b): return a * x ** b
    popt, pcov = curve_fit(func, x, mean, sigma = err, absolute_sigma = True)
    a, b = popt
    da, db = np.sqrt(np.diag(pcov))
    print(f"a = {a} +/- {da}, b = {b} +/- {db}")

    fit_x = np.array([np.min(x), np.max(x)])
    ax.plot(fit_x, func(fit_x, *popt), color = color)
    
    line, *rest = ax.errorbar(x, mean,
                    yerr = 3*err, label = plot.name, color = color, marker = ".", linestyle = 'none')
    
    for g in plot.gaps.T: 
        outliers = np.abs(g - np.nanmean(g)) > 10*sem(g, nan_policy = 'omit')
        # ax.scatter(scale(plot.Ls)[outliers], g[outliers], marker = '.', alpha = 0.2, color = line.get_color())
    # ax.boxplot(plot.gaps.T, positions = plot.Ls)

ax.set(xscale = 'log', yscale = 'log')
ax.set(ylabel = "$\Delta_{\mathrm{f}}/J$", xlabel = "System Size L")
ax.legend(frameon = False)
# ax.text(-0.25,1,'b)', transform = ax.transAxes)

fig.tight_layout()
plt.subplots_adjust(hspace=.55, left=0.22)
fig.savefig(f'./{Path.cwd().name}.svg')
fig.savefig(f'./{Path.cwd().name}.pdf')