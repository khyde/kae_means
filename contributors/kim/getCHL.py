import earthaccess
import xarray as xr
from xarray.backends.api import open_datatree
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from datetime import datetime
from datetime import timezone
auth = earthaccess.login(persist=True)

def getCHL():
    
    # Grab 8-day data @ 0.01 degree (1 km)
    tspan = ("2024-07-19", "2024-08-03")
    results = earthaccess.search_data(
        short_name="PACE_OCI_L3M_CHL_NRT",
        temporal=tspan,
        granule_name="*.8D.*.0p1deg.*",
    )
    paths = earthaccess.open(results)
    
    # Set blank list to save paths to
    ds_grid = []
    
    # For each path/file: extract ROI & save dates as variable. save in list form.
    for idx in range(len(paths)):
        dataset = xr.open_dataset(paths[idx])
        
        # Extract ROI
        dataset = dataset.isel(lon=np.where((dataset.lon.values>=-80) & (dataset.lon.values<=-45))[0],
        lat=np.where((dataset.lat.values>=20) & (dataset.lat.values<=50))[0])
    
        # Save date as coord (why not as variable?)
        d = datetime.fromisoformat(dataset.attrs['time_coverage_start'][:-1])
        ds_grid.append(dataset.assign(time = d).set_coords("time"))
    
    # convert list to nested dataset
    dataset_chl = xr.combine_nested(ds_grid,concat_dim="time")
    return dataset_chl




