import earthaccess
import xarray as xr
from xarray.backends.api import open_datatree
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from datetime import datetime
from datetime import timezone
auth = earthaccess.login(persist=True)

def get_L3_8Day(var,starttime,endtime,lonE,lonW,latN,latS):
    """
        Grab mapped L3 8-day composites at 0.01 deg resolution
        start and end dates are datetime objects
        var input as string 
        IF VAR = RRS: only grabs data for starttime
    """
    # Input datetime objects are converted to strings
    t1 = starttime.strftime('%Y-%m-%d')
    t2 = endtime.strftime('%Y-%m-%d')

    if var == "RRS":
        tspan = (t1, t1)
    else:
        tspan = (t1, t2)
    
    # Grab 8-day data @ 0.01 degree (1 km)
    results = earthaccess.search_data(
        short_name="PACE_OCI_L3M_" + var + "_NRT",
        temporal=tspan,
        granule_name="*.8D.*.0p1deg.*",
    )
    paths = earthaccess.open(results)

    # Set blank list to save paths to
    ds_grid = []
    
    # For each path/file: extract ROI. if non-Rrs fields, nest by date
    for idx in range(len(paths)):
        dataset = xr.open_dataset(paths[idx])
        
        # Extract ROI
        dataset = dataset.isel(lon=np.where((dataset.lon.values>=lonW) & (dataset.lon.values<=lonE))[0],
        lat=np.where((dataset.lat.values>=latS) & (dataset.lat.values<=latN))[0])

        # When grabbing non-Rrs fields, nest files as day "slices"
        if var != "RRS":
            # Save date as coord (why not as variable?)
            d = datetime.fromisoformat(dataset.attrs['time_coverage_start'][:-1]).astimezone(timezone.utc)
            ds_grid.append(dataset.assign(date = d).set_coords("date"))
            
            # convert list to nested dataset
            dataset = xr.combine_nested(ds_grid,concat_dim="date")
    return dataset




