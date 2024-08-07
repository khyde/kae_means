import xarray as xr
import pandas
import numpy as np
from math import exp

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
 #   if len(chl) != len(sst): 
 #       print('ERROR: the length of the CHL and SST do not match.')

    # ===> Initialize the algorithm coefficients
    match version:
        case 'v1.0': 
          sst_file = 'TURNER_PSIZE_SST_LUT_VER1.csv'
        
        case _: 
            print('ERROR: Version ' + version + ' not recognized.')

    # ===> Read the SST look up file
    sstlut = pandas.read_csv(sst_file)
    sst_table = np.array(sstlut)
     
    # ===> Convert SST values below/above the LUT min/max SST to the min/max SST in the LUT
    sst = xr.where(sst>np.max(sst_table[:,0]),np.max(sst_table[:,0]), sst)
    sst = xr.where(sst<np.min(sst_table[:,0]),np.min(sst_table[:,0]), sst)

    # ===> Find the SST value in the LUT
    sst_coeffs = sst_table[np.argmin(np.abs(sst_table[:, 0] - sst))]

    # ===> Calculate the phytoplankton size class fractions
    fpico = (sst_coeffs[3] * (1 - exp(-1 * (sst_coeffs[4] / sst_coeffs[3]) * chl))) / chl
    fnanopico = (sst_coeffs[1] * (1 - exp(-1 * (sst_coeffs[2] / sst_coeffs[1]) * chl))) / chl  
    fnano = fnanopico - fpico
    fmicro = (chl - (sst_coeffs[1] * (1 - exp(-1 * (sst_coeffs[2] / sst_coeffs[1]) * chl)))) / chl 
    
    return [fpico,fnanopico,fnano,fmicro]


            

    

    
        




