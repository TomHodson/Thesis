import pickle
import matplotlib
import matplotlib.gridspec as gridspec
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap


## Figure parameters
w = 3.375

matplotlib.rcParams.update({'font.size': 13, 
            'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})
matplotlib.rcParams.update({"axes.linewidth": 2})

with open("figure_2_gap_data.pickle", "rb") as f:
    data = pickle.load(f)
    DOS = data["DOS"]
    IPR = data["IPR"]
    taus = data["taus"]

    # globals().update(data)
    
# print(DOS, IPR)

rhos = DOS.coords["rho"]
E_bins = DOS.coords["E"]
L_i = -1
rho_i = 25
rho = rhos[rho_i]
print(f"L = Ls[L_i]")

D = DOS[dict(L = L_i)] / (E_bins[1] - E_bins[0])
mask = np.nonzero(D < 1e-1)

masked_DOS = np.array(D.copy())
masked_DOS[mask] = np.nan
masked_taus = np.array(taus.copy())
masked_taus[mask] = np.nan

print(DOS.shape, taus.shape)

cmap = matplotlib.cm.inferno.copy()
cmap.set_bad('k',1.)
pcolor_args = dict(cmap = cmap, )

f, axes = plt.subplots(nrows = 2, figsize = (5,5), sharex = "all",gridspec_kw = dict(wspace = 0.15, hspace = 0.1))
axes[0].pcolor(E_bins, rhos, masked_DOS, **pcolor_args, zorder = -1)
axes[1].pcolor(E_bins, rhos, masked_taus, **pcolor_args, zorder = -1)

ylim = (1e-3, 0.5)
axes[0].set(yscale = 'log', ylabel = r"$\rho$")
axes[1].set(yscale = 'log')
axes[0].set(ylim = ylim, xlim = (0, 1.5))
axes[1].set(ylim = ylim, xlim = (0, 1.5), yticks = [])
# axes[0].spines['right'].set_visible(False)
# axes[1].spines['left'].set_visible(False)
# axes[0].get_xaxis().set_ticks([])
# axes[1].get_yaxis().set_ticks([])
# axes[1].minorticks_off()
axes[0].vlines(x = 0, ymin = 1e-3, ymax = 1e-2, linestyles = "solid", linewidth = 4, zorder = 0, color = 'k')
axes[0].set(title = "DOS")
axes[1].set(title = r"$\tau$")

for ax in axes: ax.set_rasterization_zorder(0)

f.savefig("figure_2.pdf")
f.savefig("figure_2.svg")