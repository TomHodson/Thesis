import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib

column_width = 3.375

matplotlib.rcParams.update({'font.size': 13, 'text.usetex': True, 'font.family': 'serif', 'font.serif': ['Computer Modern']})

data_hlm_field = np.load('dos_oscillations_hlm_field.npy', allow_pickle=True).tolist()
data_amo_nofield = np.load('dos_oscillations_am_nofield.npy', allow_pickle=True).tolist()
xdata = np.load('xdata.npy')
xdata = (xdata[:-1] + xdata[1:]) / 2.0

system_sizes = data_amo_nofield.keys()
line_colors = [cm.inferno(X) for X in [0.25, 0.5, 0.75]]

fig, axes = plt.subplots(nrows=2, ncols=1)
fig.set_size_inches(column_width, 1.3*column_width)

# SET UP AXES

axes[0].set_xscale("log")
axes[1].set_xscale("log")
axes[0].set_xticks([])
axes[0].axes.xaxis.set_visible(False)

axes[0].set_yticks([1.00, 1.25, 1.50, 1.75])
# axes[0].set_ylabel(r"$\rho(E)$ [arb. units]")
# Hack in shared y-label
fig.text(0.02, 0.5, r"$\rho(E)$ [arb. units]", va='center', rotation='vertical')
axes[1].set_yticks([1.00, 1.25, 1.50, 1.75])
axes[1].set_xlabel(r"$E$")



# PLOT DATA

for system_size, line_color in zip(system_sizes, line_colors):
  shared_args = {
    'c': line_color,
    'alpha': 0.7,
    'fmt': '.',
    'capsize': 2,
    'markersize': 2
  }

  hlm_vals = data_hlm_field[system_size]
  amo_vals = data_amo_nofield[system_size]
  
  axes[0].errorbar(
    xdata, hlm_vals[0], hlm_vals[1], label=f"$L={system_size}$", **shared_args
  )

  axes[1].errorbar(
    xdata, amo_vals[0], amo_vals[1], **shared_args
  )

axes[0].legend()

# TWEAKS + SAVE

plt.tight_layout()
plt.subplots_adjust(hspace=.0, left=0.22)

plt.savefig('dos_oscillations.pdf')