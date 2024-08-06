
import xarray as xr
from datetime import datetime
from datetime import date
from datetime import timedelta

def SST8day(start_date,end_date=date.today()-timedelta(days=8),
            latmin=20,latmax=50,lonmin=-80,lonmax=-45,
            variable='sea_surface_temperature'):
    """
    PURPOSE: Function to download SST data and return 8-day means
    REQUIRED INPUTS: 
      START_DATE..... First date of the date range
      
    OPTIONAL INPUTS
      END_DATE....... End date of the date range (default is today's date)
      LATMIN......... Minimum latitude of the boundingn box
      LATMAX......... Maximum latidue of the boundingn box
      LONMIN......... Minimum longitude of the boundingn box
      LONMAX......... Maximum longitude of the boundingn box

    KEYWORDS

    OUTPUTS

    EXAMPLES

    NOTES

    COPYRIGHT: 
        Copyright (C) 2024, Department of Commerce, National Oceanic and Atmospheric Administration, National Marine Fisheries Service,
        Northeast Fisheries Science Center, Narragansett Laboratory.
        This software may be used, copied, or redistributed as long as it is not sold and this copyright notice is reproduced on each copy made.
This routine is provided AS IS without any express or implied warranties whatsoever.

    AUTHOR:
      This program was written on August 06, 2024 by Kimberly J. W. Hyde, Northeast Fisheries Science Center | NOAA Fisheries | U.S. Department of Commerce, 28 Tarzwell Dr, Narragansett, RI 02882
  
    MODIFICATION HISTORY:
        Aug 06, 2024 - KJWH: Initial code written
    """
    
    # Get the data
    # TODO: make the erddap url an input variable that defaults to this url. Should use the NRT for recent data, but the reanalysis product for later dates
    erddap_url = '/'.join(['https://comet.nefsc.noaa.gov',
                       'erddap',
                       'griddap',
                       'noaa_coastwatch_acspo_v2_nrt'
                       ])
    ds = xr.open_dataset(erddap_url)
    ds_subset = ds[variable].sel(time=slice(start_date, end_date),
                                                  latitude=slice(latmax,latmin),
                                                  longitude=slice(lonmin,lonmax), 
                                                )

    
    ds_subset.load()
    ds_8day = ds_subset.resample(time='8d').mean(dim='time')
    
    return ds_8day

