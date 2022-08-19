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
matplotlib.rcParams.update({"axes.linewidth": 1})

with open("figure_2_gap_data.pickle", "rb") as f:
    data = pickle.load(f)
    DOS = data["DOS"]
    IPR = data["IPR"]
    taus = data["taus"]

def plot_fermion_gap_scaling(ax):
    @dataclass
    class PlotData:
        name: str
        location: str
        Ls = None
        gaps = None

    with open("gap_vs_L_aggregated.pickle", 'rb') as f:
        plot_data = pickle.load(f)

    line_colors = [cm.inferno(X) for X in [0.25, 0.5, 0.75]]
    ax.set(ylabel = "$\Delta_{\mathrm{f}}/J$", xlabel = r"Vortex Density $\rho$")

    for plot,color in zip(plot_data, line_colors[::2]):
        
        line, *rest = ax.errorbar(scale(plot.Ls), np.nanmean(plot.gaps, axis = -1), 
                        yerr = 6*sem(plot.gaps, axis = -1, nan_policy = 'omit'), 
                        label = plot.name, color = color, marker = ".")
        
        for g in plot.gaps.T: 
            outliers = np.abs(g - np.nanmean(g)) > 10*sem(g, nan_policy = 'omit')
            ax.scatter(scale(plot.Ls)[outliers], g[outliers], marker = '.', alpha = 0.2, color = line.get_color())
        # ax.boxplot(plot.gaps.T, positions = plot.Ls)

    ax.set(xscale = 'log', yscale = 'log')
    ax.set(ylabel = "$\Delta_{\mathrm{f}}/J$", xlabel = "System Size L")
    ax.legend(frameon = False)



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


## Set up the figure and the top level gridspec
fig = plt.figure(figsize = (1.2*w, w))
gs = gridspec.GridSpec(nrows = 2, ncols = 2, figure=fig, 
                       width_ratios = (20,1), 
                       hspace = 0.05,
                       wspace = 0.1,
                       )

## main panel splits into 2x2 for colorbars and DOS/tau
DOS_ax = fig.add_subplot(gs[0, 0])
DOS_cmap_ax  = fig.add_subplot(gs[0, 1])

tau_ax = fig.add_subplot(gs[1, 0])
tau_cmap_ax  = fig.add_subplot(gs[1, 1])

# inset
# from mpl_toolkits.axes_grid1.inset_locator import inset_axes
# gap_scaling_ax = inset_axes(tau_ax, width=0.7, height=0.7, loc = 1, borderpad = 0.2)
# gap_scaling_ax.tick_params(axis="y",direction="in", pad=-50)
# gap_scaling_ax.tick_params(axis="x",direction="in", pad=-50)

# DOS pcolor
cmap = matplotlib.cm.inferno
DOScolorable = DOS_ax.pcolor(E_bins, rhos, masked_DOS, zorder = -1, cmap = cmap)
fig.colorbar(DOScolorable, cax=DOS_cmap_ax, orientation = "vertical")
DOS_cmap_ax.set(ylabel = r"DOS")

# tau pcolor
cmap = matplotlib.cm.inferno
norm = matplotlib.colors.Normalize(vmin = -1, vmax = 0)
taucolorable = tau_ax.pcolor(E_bins, rhos, masked_taus, cmap=cmap, norm=norm, zorder = -1)
fig.colorbar(taucolorable, cax=tau_cmap_ax, orientation = "vertical")
tau_cmap_ax.set(ylabel = r"$\tau$", yticks = [0, -0.5, -1], yticklabels = ["0", "-0.5", "-1"])

ylim = (1e-2, 0.5)
DOS_ax.set(yscale = 'log')
tau_ax.set(yscale = 'log')
DOS_ax.set(ylim = ylim, xlim = (0, 1.5))
tau_ax.set(ylim = ylim, xlim = (0, 1.5))

DOS_ax.set(xticks = [])
tau_ax.set(xlabel = "Energy $E/J$")

fig.text(0.075, 0.5, r"Flux defect density $\rho$", ha = "right", va = "center", rotation = 90)

for ax in [DOS_ax, tau_ax]: ax.set_rasterization_zorder(0)

plt.subplots_adjust(left = 0.25, bottom = 0.15, right = 0.82)

fig.savefig("figure_2.pdf", dpi = 400)
fig.savefig("figure_2.svg", dpi = 400)