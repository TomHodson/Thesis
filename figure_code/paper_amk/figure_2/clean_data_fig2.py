##### Use this script with the 200mb file all_data.pickle that was generated on cx1
import numpy as np
from numpy.polynomial import Polynomial as Poly
from tqdm import tqdm
import pickle
import xarray as xr

with open("/Users/tom/all_data.pickle", "rb") as f:
    data = pickle.load(f)
    

globals().update(data["orginal_config"])

# label the data
DOS = xr.DataArray(data["DOS"], coords=[Ls, np.arange(N_realisations), rhos, E_bins[:-1]], dims=["L", "realisation", "rho", "E"])
IPR = xr.DataArray(data["IPR"], coords=[Ls, np.arange(N_realisations), rhos, qs, E_bins[:-1]], dims=["L", "realisation", "rho", "q", "E"])

# Clean up the data
L_slice = slice(4,-7)
DOS = DOS.mean(dim = "realisation", skipna=True)[dict(L = L_slice)]
IPR = IPR.mean(dim = "realisation", skipna=True)[dict(L = L_slice, q = 0)]
Ls = Ls[L_slice]


#compute taus
taus = np.NaN * np.zeros(shape = (len(rhos), len(E_bins) - 1))
taus = xr.DataArray(taus, coords = [rhos, E_bins[:-1]], dims = ["rho", "E"])

for rho_i, rho in tqdm(enumerate(rhos), total = len(rhos)):
    idx = np.where(np.all(np.isfinite(IPR[:, rho_i]), axis = 0))[0]
    for E_i in idx:
        E = E_bins[E_i]
        p = Poly.fit(np.log(DOS.coords["L"]), np.log(IPR[:, rho_i, E_i]), deg = 1)
        taus[rho_i, E_i] = p.coef[1]
        
figure_2_gap_data= dict(
    original_config = data["orginal_config"],
    DOS = DOS,
    IPR = IPR,
    Ls = Ls,
    taus = taus,
)

with open("./figure_2_gap_data.pickle", "wb") as f:
    pickle.dump(figure_2_gap_data, f)