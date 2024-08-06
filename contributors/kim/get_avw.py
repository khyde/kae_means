# This function is written to extract Apparent Visible Wavelength from nc files downloaded from NASA Ocean Colour Browser
# Created by Kitty Kam

# Import library
import earthaccess
import xarray as xr
from xarray.backends.api import open_datatree
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import os
from datetime import datetime, timezone


# function
def get_avw():

    python_dir = '/home/jovyan/shared-public/KAE_means/'
    # get paths of the nc files in "AVW data" folder
    paths = [python_dir+"AVW data/PACE_OCI.20240719_20240726.L3m.8D.AVW.V2_0.NRT.x_avw.nc", 
             python_dir+"AVW data/PACE_OCI.20240727_20240803.L3m.8D.AVW.V2_0.NRT.x_avw.nc"]
    
    # open an empty list to save each dataset 
    ds_grid = []

    # for loop
    for i in range(len(paths)):
        #open dataset
        #print(paths[i])
        dataset = xr.open_dataset(paths[i])

        # pull out the start date of 8-days average, convert it into datetime format
        d = datetime.fromisoformat(dataset.attrs['time_coverage_start'][:-1]).astimezone(timezone.utc)
        # (1) add date as new varible, 
        # (2) set date as part of coordinates, 
        # (3) save it into the dataset, 
        # (4) add the modified dataset into the list 
        ds_grid.append(dataset.assign(date = d).set_coords('date'))

    # create a nested dataset (3D)
    ds_all = xr.combine_nested(ds_grid, concat_dim ="date") # set date as the identifing index

    # return the nested dataset
    return ds_all

