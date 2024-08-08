import earthaccess
import xarray as xr
from xarray.backends.api import open_datatree
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from datetime import datetime, timezone
from random import randint
auth = earthaccess.login(persist=True)


# What this does:
# (1) import a Rrs (3D) dataset to calculate mean and sd
# (2) plot Rrs vs wv 
# (3) save the plot in the same directory

# *** make sure dataset and flag have the same dimension of lat and lon

def Rrs_avg(dataset,flag, n, plot_flag = False):
    # dataset = 3D dataset (not nested)
    # flag = 2D array flag
    # n = desired flag
    
    # create True/False mask depeneding on the chosen cluster (flag)
    mask = flag == n
    
    # pull the Rrs from the selected location
    Rrs = dataset.Rrs.values[mask]
    wv = dataset.wavelength

    # calculate mean and sd
    mean = np.nanmean(Rrs,axis = 0)
    sd = np.nanstd(Rrs, axis = 0)

    # plot
    if plot_flag == True:
        fig, ax = plt.subplots(1)
        ax.plot(wv, mean, lw=2, color='blue')
        ax.fill_between(wv, mean+sd, mean-sd, facecolor='blue', alpha=0.5)
        ax.set_title(r'Rrs spectral average : {} to {}'.format(datetime.fromisoformat(dataset.attrs['time_coverage_start'][:-1]).astimezone(timezone.utc).strftime("%Y-%m-%d"),
                                                                   datetime.fromisoformat(dataset.attrs['time_coverage_end'][:-1]).astimezone(timezone.utc).strftime("%Y-%m-%d")))
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('$R_{rs} \ (sr^{-1})$')
        ax.grid()
    
        # save plot
        plt.savefig('Rrs_avg_{}_{}.png'.format(datetime.fromisoformat(dataset.attrs['time_coverage_start'][:-1]).astimezone(timezone.utc).strftime("%Y-%m-%d"),
                                                                   datetime.fromisoformat(dataset.attrs['time_coverage_end'][:-1]).astimezone(timezone.utc).strftime("%Y-%m-%d")))
        
    # return metrics : mean, sd and wavelength
    return mean, sd, wv





