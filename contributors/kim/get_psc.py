import xarray as xr
import pandas
import numpy as np
from datetime import datetime
from getSST8day import SST8day
from get_L3_8Day import get_L3_8Day

def run_psc(start_date,end_date,eightday=1):
    """
    PURPOSE: To get the CHL and SST data and run the PHYTO_SIZE_TURNER model to calculate phytoplankton size classes using the Northeast U.S. regionally tuned phytoplankton size class algorithm based on Turner et al. (2021).
    
    REQUIRED INPUTS: 
      START_DATE.... The start date for getting the file
      
    OPTIONAL INPUTS
      END_DATE...... The end date for getting the files

    KEYWORDS:
      EIGHTDAY... Set to use 8-day mean data (default=1)
      NETCDF..... Set to output a netcdf of the data

    OUTPUTS
      Phytoplankton size class (micro,nano, and picoplankton fractions and input chlorophyll data.
    
    EXAMPLES:

    NOTES:
      To calculate phytoplankton size class chlorophyll contribution, multiply total chlorophyll with each size class fraction.

    COPYRIGHT: 
        Copyright (C) 2024, Department of Commerce, National Oceanic and Atmospheric Administration, National Marine Fisheries Service,
        Northeast Fisheries Science Center, Narragansett Laboratory.
        This software may be used, copied, or redistributed as long as it is not sold and this copyright notice is reproduced on each copy made.
This routine is provided AS IS without any express or implied warranties whatsoever.

    AUTHOR:
      This program was written on August 08, 2024 by Kimberly J. W. Hyde, Northeast Fisheries Science Center | NOAA Fisheries | U.S. Department of Commerce, 28 Tarzwell Dr, Narragansett, RI 02882
  
    MODIFICATION HISTORY:
        Aug 08, 2024 - KJWH: Initial code written
    """

    # ===> Get the chlorohyll data and extract the array
    chl = get_L3_8Day(CHL,start_date,end_date)
    chlarr = chl['chlor_a']

    # ===> Get the SST data, regrid to the chlorophyll and extract the array
    sst = SST8day(start_date,end_date)
    sstarr = sst.interp(latitude=chlarr["lat"],longitude=chlarr["lon"],method='nearest')
    # ===> Run the phytoplankton size class model
    psize = psc(chlarr,sstarr)

    # TODO If keyword is set to save as netcdf then psize.to_netcdf("psize_output.nc")

    return psize

    

    