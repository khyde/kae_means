import xarray as xr
import pandas

def psc(chl,sst,version='v1.0'):
    """
    PURPOSE: Function to calculate phytoplankton size classes using the Northeast U.S. regionally tuned phytoplankton size class algorithm based on Turner et al. (2021)
    
    REQUIRED INPUTS: 
      CHL....... Chlorophyll data
      SST....... Sea surface temperature data
      
    OPTIONAL INPUTS
      VERSION... Version of the code to run

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

    # ===> Look for CHL & SST and make sure the data arrays match
    if len(chl) != len(sst): 
        print('ERROR: the length of the CHL and SST do not match.')

    # ===> Initialize the algorithm coefficients
    match version:
        case 'v1.0': 
          coeff1 = 0.8337
          coeff2 = 0.7830
          coeff3 = 0.1984
          coeff4 = 0.3956
          sst_file = 'TURNER_PSIZE_SST_LUT_VER1.csv'
        
        case _: 
            print('ERROR: Version ' + VERSION + ' not recognized.')

    # ===> Read the SST look up file
    sst_table = pandas.read_csv(sst_file)

            

    

    
        




