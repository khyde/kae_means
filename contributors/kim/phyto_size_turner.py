import xarray as xr
import pandas
import numpy as np
from datetime import datetime

def psc(chl,sst,version='v1.0'):
    """
    PURPOSE: Function to calculate phytoplankton size classes using the Northeast U.S. regionally tuned phytoplankton size class algorithm based on Turner et al. (2021)
    
    REQUIRED INPUTS: 
      CHL....... Chlorophyll data
      SST....... Sea surface temperature data
      
    OPTIONAL INPUTS
      VERSION... Version of the look up file to use

    KEYWORDS:
      None

    OUTPUTS
      Phytoplankton size class (micro,nano, and picoplankton fractions and input chlorophyll.

    REQUIRED FILES:
      TURNER_PSIZE_SST_LUT_VER1.csv
    
    EXAMPLES:

    NOTES:
      To calculate phytoplankton size class chlorophyll contribution, multiply total chlorophyll with each size class fraction.

    REFERENCE:
      Turner, K. J., C. B. Mouw, K. J. W. Hyde, R. Morse, and A. B. Ciochetto (2021), Optimization and assessment of phytoplankton size class algorithms for ocean color data on the Northeast U.S. continental shelf, Remote Sensing of Environment, 267, 112729, [doi:https://doi.org/10.1016/j.rse.2021.112729]
    COPYRIGHT: 
        Copyright (C) 2024, Department of Commerce, National Oceanic and Atmospheric Administration, National Marine Fisheries Service,
        Northeast Fisheries Science Center, Narragansett Laboratory.
        This software may be used, copied, or redistributed as long as it is not sold and this copyright notice is reproduced on each copy made.
This routine is provided AS IS without any express or implied warranties whatsoever.

    AUTHOR:
      This program was written on August 06, 2024 by Kimberly J. W. Hyde, Northeast Fisheries Science Center | NOAA Fisheries | U.S. Department of Commerce, 28 Tarzwell Dr, Narragansett, RI 02882
  
    MODIFICATION HISTORY:
        Aug 06, 2024 - KJWH: Initial code written
        Aug 08, 2024 - KJWH: Updated how the coefficients are extracted and the data are returned
    """

def psc(chlarr,sstarr):
    
    # ===> Get the SST look-up file (can be updated with new LUT versions)
    match version:
        case 'v1.0': 
          sst_file = 'TURNER_PSIZE_SST_LUT_VER1.csv'
        
        case _: 
            print('ERROR: Version ' + version + ' not recognized.')

    
    sstlut = pandas.read_csv(sst_file,index_col='SST')
    sstlut = sstlut.to_xarray()
    
    # ===> Find the coefficients from the LUT based on the input SST
    sst_coeffs = sstlut.sel({"SST": sstarr}, method="nearest")

    # ===> Calculate the phytoplankton size class fractions
    fpico = (sst_coeffs.COEFF3 * (1 - np.exp(-1 * (sst_coeffs.COEFF4 / sst_coeffs.COEFF3) * chlarr))) / chlarr
    fnanopico = (sst_coeffs.COEFF1 * (1 - np.exp(-1 * (sst_coeffs.COEFF2 / sst_coeffs.COEFF1) * chlarr))) / chlarr  
    fnano = fnanopico - fpico
    fmicro = (chlarr - (sst_coeffs.COEFF1 * (1 - np.exp(-1 * (sst_coeffs.COEFF2 / sst_coeffs.COEFF1) * chlarr)))) / chlarr 

    phyto = xr.Dataset({"fmicro":fmicro,"fnano":fnano,"fpico":fpico,"chlor_a":chlarr})
    
    return phyto
    


            

    

    
        




