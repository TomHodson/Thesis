import matplotlib
from matplotlib import cm
from matplotlib.colors import to_rgba, to_hex
from matplotlib import pyplot as plt

# see https://matplotlib.org/stable/tutorials/text/usetex.html
matplotlib.rcParams.update({
    "font.size": 12,
    "text.usetex": True,
    "axes.linewidth": 1.2,
    'font.family': 'serif',
    'font.serif': ['cmr10'],
    'font.weight': 'ultralight',
    "axes.formatter.use_mathtext" : True,
})

bond_colors = """" 
#e41a1c
#4daf4a
#00639a
""".split()[1:]

line_colors = [to_hex(a) for a in cm.inferno([0.25, 0.5, 0.75])]
plaq_color_scheme = plt.get_cmap("tab10")([0,1])


