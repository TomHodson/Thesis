#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import subprocess
from tqdm import tqdm

from koala import plotting as pl
from koala import flux_finder
from koala import example_graphs as eg
from koala.flux_finder import pathfinding

column_width = w = 3.375
black_line_widths = 1.2

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.expanduser('~/git/Thesis/figure_code')))
from plot_settings import bond_colors, plaq_color_scheme, dual_color

rng = np.random.default_rng(222424252565)

subprocess.run(["mkdir", "-p", "./animation"])

for i in tqdm(range(10)):

    lattice, colouring, ujk_ground_state = eg.make_amorphous(8, rng = rng)
    # lattice, colouring, ujk_ground_state = eg.make_honeycomb(7)

    ground_state_fluxes = flux_finder.fluxes_from_bonds(lattice, ujk_ground_state)

    #create a bond_sector state in the bond sector
    bond_sector_ujk = rng.choice([+1, -1], size = ujk_ground_state.shape)
    bond_sector_fluxes = flux_finder.fluxes_from_bonds(lattice, bond_sector_ujk)

    # create a reference state to fix the gauge
    reference_ujk = np.ones_like(bond_sector_ujk)
    reference_fluxes = flux_finder.fluxes_from_bonds(lattice, reference_ujk)

    # construct the bond_sector state using just MSP bond flips from the reference
    # possibly in a different gauge sector and/or topological sector
    flux_sector_ujk = flux_finder.find_flux_sector(lattice, bond_sector_fluxes, reference_ujk)
    flux_sector_fluxes = flux_finder.fluxes_from_bonds(lattice, flux_sector_ujk)

    # Construct the gauge sector, this is just the difference between
    # the bond sector and the flux
    gauge_sector_ujk = bond_sector_ujk * flux_sector_ujk
    gauge_sector_fluxes = flux_finder.fluxes_from_bonds(lattice, gauge_sector_ujk)
    assert(np.all(np.equal(bond_sector_fluxes, flux_sector_fluxes)))

    ## Construct the topological sector
    verts_x, Px, dir_x = pathfinding.graph_loop(lattice, direction = "x")
    verts_y, Py, dir_y = pathfinding.graph_loop(lattice, direction = "y")

    plaqs_x, Tx = pathfinding.dual_loop(lattice, direction = "x")
    plaqs_y, Ty = pathfinding.dual_loop(lattice, direction = "y")

    def measure(ujk, edges, directions):
        return np.product(ujk[edges] * directions)

    Mx = measure(gauge_sector_ujk, Px, dir_x)
    My = measure(gauge_sector_ujk, Py, dir_y)

    topological_sector_ujk = np.ones_like(bond_sector_ujk)

    if Mx == -1: 
        gauge_sector_ujk[Ty] *= -1
        topological_sector_ujk[Ty] *= -1
        
    if My == -1: 
        gauge_sector_ujk[Tx] *= -1
        topological_sector_ujk[Tx] *= -1

    topological_sector_fluxes = flux_finder.fluxes_from_bonds(lattice, topological_sector_ujk)
        
    Mx = measure(gauge_sector_ujk, Px, dir_x)
    My = measure(gauge_sector_ujk, Py, dir_y)

    assert(all(np.equal(bond_sector_ujk, flux_sector_ujk * gauge_sector_ujk * topological_sector_ujk * reference_ujk)))

    ncols = 4
    fig, axes = plt.subplots(nrows=1, ncols=ncols)
    fig.set_size_inches(2 * w, 2/3.5 * w)

    ax = axes[0]
    pl.plot_edges(lattice, directions = bond_sector_ujk, 
                labels = (bond_sector_ujk != reference_ujk),
                color_scheme = ['grey', 'black'],
                ax = ax, linewidths = black_line_widths, 
                )

    pl.plot_plaquettes(lattice, labels = (bond_sector_fluxes != reference_fluxes),
                    color_scheme = plaq_color_scheme, ax = ax, alpha = 0.5)

    ax = axes[1]
    pl.plot_edges(lattice, labels = (flux_sector_ujk != reference_ujk),
                ax = ax, linewidths = black_line_widths,
                color_scheme = ['grey', 'black'])

    pl.plot_plaquettes(lattice, labels = (flux_sector_fluxes != reference_fluxes),
                    color_scheme = plaq_color_scheme, ax = ax, alpha = 0.5)

    flipped_edges = (flux_sector_ujk != reference_ujk)
    pl.plot_dual(lattice, subset = flipped_edges, ax = ax, linewidths = black_line_widths, color_scheme = dual_color)

    ax = axes[2]

    pl.plot_edges(lattice, labels = (gauge_sector_ujk != reference_ujk),
                ax = ax, linewidths = black_line_widths,
                color_scheme = ['grey', 'black'])

    flipped_edges = (gauge_sector_ujk != reference_ujk)
    pl.plot_dual(lattice, subset = flipped_edges, ax = ax,
                linewidths = black_line_widths, color_scheme = dual_color)

    pl.plot_plaquettes(lattice, labels = (gauge_sector_fluxes != reference_fluxes),
                    color_scheme = ['white', 'red'], ax = ax, alpha = 0.5)

    ax = axes[3]
    pl.plot_edges(lattice, ax = ax, linewidths = black_line_widths, color = 'grey')

    # pl.plot_plaquettes(lattice, subset = plaqs_x, color = 'grey', alpha = 0.5)
    # pl.plot_dual(lattice, subset = Tx)
    # pl.plot_edges(lattice, subset = Tx)

    # pl.plot_edges(lattice, subset = Py, directions = dir_y)

    pl.plot_plaquettes(lattice, labels = (topological_sector_fluxes != reference_fluxes),
                    color_scheme = ['white', 'red'], ax = ax, alpha = 0.5)

    flipped_edges = (topological_sector_ujk != reference_ujk)
    if np.any(flipped_edges):
        pl.plot_dual(lattice, subset = flipped_edges, ax = ax, linewidths = black_line_widths, color_scheme = dual_color)
        pl.plot_edges(lattice, subset = flipped_edges, ax = ax, linewidths = black_line_widths, color = 'k')


    for ax in axes: ax.set(xticks = [], yticks = [])

    axes[0].set(title = "Bond Sector")
    axes[1].set(title = "Flux Sector")
    axes[2].set(title = "Gauge Field")
    axes[3].set(title = "Topological Sector")


    fig.tight_layout()

    if i == 0: 
        fig.savefig(f'./{Path.cwd().name}.svg', transparent = True)
        fig.savefig(f'./{Path.cwd().name}.pdf')
    fig.savefig(f"animation/iteration_{i:03}.svg")
    plt.close(fig)

print("Making the gif...")
subprocess.run(["magick", "animation/*.svg", f'./{Path.cwd().name}.gif'])
subprocess.run(["convert", "-delay", "200", f'./{Path.cwd().name}.gif', f'./{Path.cwd().name}.gif'])
subprocess.run(["rm", "-r", "./animation"])

