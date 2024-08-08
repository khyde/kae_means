import xarray as xr
import numpy as np
import pandas as pd

# Goal: to calculate normalized fluorescence line height from Rrs and F0 constant
# Description  : https://oceancolor.gsfc.nasa.gov/resources/atbd/nflh/
# Solar irradiance spectrum [F0] uses TSIS-1 version : https://oceancolor.gsfc.nasa.gov/resources/docs/rsr_tables/

def get_nFLH(Rrs):
    # Rrs is a 3D dataset

    # read F0 file
    F0_table = pd.read_csv('functions/f0_tsis.txt', skiprows = 15, header = None, names= ['wv','F0'], sep = ' ')

    # Calculate nLw using this relationship: nLw = Rrs x F0
    lambda1 = 678; lambda2 = 660; lambda3=706
    nLw_678 = Rrs.sel({"wavelength": lambda1}) * F0_table.loc[F0_table.loc[:,"wv"]==lambda1,"F0"].values[0]  #Fluorescence band
    nLw_660 = Rrs.sel({"wavelength": lambda2}) * F0_table.loc[F0_table.loc[:,"wv"]==lambda2,"F0"].values[0]  # shorter band
    nLw_705 = Rrs.sel({"wavelength": lambda3}) * F0_table.loc[F0_table.loc[:,"wv"]==lambda3,"F0"].values[0]  # longer band

    # Calculate nFLH
    # based on Zhao et al. (2022): https://www.mdpi.com/2072-4292/14/11/2511
    nFLH = nLw_678 - (lambda3 - lambda1)/(lambda3 - lambda2) * nLw_660 - (lambda1 - lambda2)/(lambda3 - lambda2) * nLw_705

    # output (2D)
    return nFLH
