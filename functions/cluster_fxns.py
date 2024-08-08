from gapstatistics.gapstatistics import GapStatistics
import argopy
from argopy import DataFetcher  # This is the class to work with Argo data
from argopy import ArgoIndex  #  This is the class to work with Argo index
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from scipy.spatial import KDTree
from xarray.backends.api import open_datatree
import xarray as xr

from get_L3_8Day import get_L3_8Day
from get_avw import get_avw
from getSST8day import SST8day
from datetime import datetime

# Make sure to pip install before
def GetOptimalK(max_K, data):

    """
        use gapstatistics package to determine optimal number of clusters
        for K-means clusterting

        INPUTS:
        - max_K: max # of clusters to evaluate 0...max_K
        - data: input data used to train cluster

        OUTPUT:
        - gs: gapstatistics object
        - optimum: determined optimum number of clusters from gap statistics
    """
    gs = GapStatistics(distance_metric='minkowski')
    
    optimum = gs.fit_predict(K=10, X=data)
    
    return gs, optimum


def GetSurfaceFloatValues(region, date_range, target_parameters, want_all=True):

    """
        Get surface values (defined as upper 50m) for all profiles in a given region and 
        data range. QC flags 1 and 2 are used

        INPUTS
        - region: bounding region given in the floowing order [latN, latS, lonE, lonE]
        - date range: date limits [start_date, end_date]
        - target_parameters: list of BGC-Argo parameters ['DOXY','BBP700',..]
        - want_all:
            - if True, will return floats that have only ALL of the listed parameters
            - if False, will return floats that have any parameters

        OUTPUTS
        - idx file with mean float values appended as 'PARAM_FLOAT'
    """
    
    # Initial set up
    argopy.set_options(src='erddap', mode='expert');
    idx = ArgoIndex(index_file='bgc-s').load().to_dataframe()
    
    latN = region[0]; latS = region[1]; lonW = region[2]; lonE = region[3]
    good_inds = []
    surf_depth = 50
    
    for pi in np.arange(idx.shape[0]):
    
        param_count = 0
        for ti in np.arange(len(target_parameters)):
            
            if target_parameters[ti] in idx.loc[:, 'parameters'].values[pi].split(' '):
                param_count = param_count +1

        if want_all == True:
            if param_count == len(target_parameters):
                good_inds.append(pi)
        else:
            if param_count > 0:
                good_inds.append(pi)
    
    good_idx = idx.iloc[good_inds,:]
    
    # Crop to target region and time
    # Crop to target time period and region
    good_idx = good_idx.loc[(good_idx.loc[:,'date']>=pd.Timestamp(date_range[0])) & \
    (good_idx.loc[:,'date']<=pd.Timestamp(date_range[1])), :]
    
    latN = 50; latS = 20; lonW = -80; lonE = -45
    
    good_idx = good_idx.loc[(good_idx.loc[:,'latitude']<=latN) & (good_idx.loc[:,'latitude']>=latS) & \
    (good_idx.loc[:,'longitude']<=lonE) & (good_idx.loc[:,'longitude']>=lonW), :]

    ## 
    float_values = np.zeros((good_idx.shape[0], len(target_parameters)))*np.NaN

    # Download float data
    for fi in np.arange(float_values.shape[0]):
    #for fi in np.arange(10):
        fname = good_idx.loc[:,'file'].values[fi]
        
        wmo = int(fname.split('/')[1])
        profnum = int(fname.split('_')[-1].split('.')[0][:3])
    
        print(wmo, profnum)
        
        float_data = DataFetcher(ds='bgc', src = 'gdac').profile(wmo, profnum).load().data.to_dataframe()
        # Get surface data
        float_data = float_data.loc[float_data.loc[:,'PRES']<=surf_depth,:]
        
        
        # QC
        for ti in np.arange(len(target_parameters)):

            if target_parameters[ti] in good_idx.loc[:, 'parameters'].values[fi].split(' '):
                
                float_data.loc[(float_data.loc[:,target_parameters[ti]+'_ADJUSTED_QC']!=1) & \
                (float_data.loc[:,target_parameters[ti]+'_ADJUSTED_QC']!=2), target_parameters[ti]+'_ADJUSTED']=np.NaN
        
                float_values[fi, ti] = float_data.loc[:,target_parameters[ti]+'_ADJUSTED'].mean()
    # Append data
    # Temporarily save data because it takes awhile to get this
    # Append to index file
    for pi in np.arange(len(target_parameters)):
        good_idx = good_idx.assign(**{target_parameters[pi]+'_FLOAT': float_values[:,pi]})
    return good_idx

def Regrid(high_res_data, high_res_grid, target_grid):

    """
        Regridding function used to subsample a higher res. grid to a lower one
        using griddata

        INPUTS
        - high_res_data: data to be mapped
        - high_res_grid: [high_res_lon, high_res_lat]
        - target_grid: [target_lon, target_lat]

        OUTPUTS
        - data: high_res_data regridded to target
    """

    data = np.zeros((high_res_data.shape[0], target_grid[0].shape[0], target_grid[0].shape[1]))*np.NaN

    LO, LA = np.meshgrid(high_res_grid[0],high_res_grid[1])
    points = (LO.flatten(), LA.flatten())
    
    for i in np.arange(data.shape[0]):
        data[i, :,:] = griddata(points, high_res_data[i].flatten(), target_grid, method ='nearest')

    return data

def GetData(latN, latS, lonW, lonE, date_range):

    
    """
        Get PACE data for in specific region and time period. This function calls other functions to get data
        for two 8 day periods. Note: THERE ARE HARDCODED DATES. Def. can be further improved

        INPUTS
        - bounding regions (latN, latS, lonW, lonE)
        - date range: date limits [start_date, end_date]

        OUTPUTS
        - SST: sea surface temperature)
        - AVW: apparent visible wavelength
        - CHL: chlrorophyll a
        - POC: particulate organic carbon
        - KD: diffuse attenuation 
        - RRS: remote sensing reflectance
    """

    SST = SST8day(date_range[0],date_range[1])
    AVW = get_avw() # Notes: AVW is at higher resolution grid...need to down size
    CHL = get_L3_8Day('CHL',datetime.strptime(date_range[0],'%Y-%m-%d'),
                      datetime.strptime(date_range[1],'%Y-%m-%d'),lonE,lonW,latN,latS)
    POC = get_L3_8Day('POC',datetime.strptime(date_range[0],'%Y-%m-%d'),
                      datetime.strptime(date_range[1],'%Y-%m-%d'),lonE,lonW,latN,latS)
    KD = get_L3_8Day('KD',datetime.strptime(date_range[0],'%Y-%m-%d'),
                      datetime.strptime(date_range[1],'%Y-%m-%d'),lonE,lonW,latN,latS)

    # Download Rrs
    # NOTE: HARDCODED DATE
    RRS1 = get_L3_8Day('RRS',datetime.strptime(date_range[0],'%Y-%m-%d'),
                      datetime.strptime(date_range[1],'%Y-%m-%d'),lonE,lonW,latN,latS)
    RRS2 = get_L3_8Day('RRS',datetime.strptime('2024-07-27','%Y-%m-%d'),
                      datetime.strptime(date_range[1],'%Y-%m-%d'),lonE,lonW,latN,latS)

    RRS = [RRS1, RRS2]
    return SST, AVW, CHL, POC, KD, RRS

# Get cluster labels
def GetClosestCluster(LO,LA, total_labels, target_lat, target_lon, dates):

    tree = KDTree(np.c_[LO.ravel(),LA.ravel()])
    labels = np.zeros(target_lon.shape[0])*np.NaN
    
    for ti in np.arange(target_lat.shape[0]):
        dd, ii = tree.query([target_lon[ti],target_lat[ti]])
    
        # Get data period 
        if dates[ti] < np.datetime64('2024-07-27'):
            si = 0
        else:
            si = 1
    
        inds = np.unravel_index(ii,LO.shape)
        labels[ti] = total_labels[si,inds[0], inds[1]]
    return labels

def GetMOANAMeans(flist, optimum_k, LO, LA, total_labels):
    pcc_list =[ 'picoeuk_moana','prococcus_moana','syncoccus_moana']

    # Calculate averages 
    moana_results = np.zeros((optimum_k, len(pcc_list),3))

    for fname in flist:
    #for fname in [flist[0]]:
        datatree = open_datatree(fname)
        dataset = xr.merge(datatree.to_dict().values())
        
        all_labels = np.zeros(dataset.longitude.values.shape)*np.NaN
        good_inds = np.where(np.isnan(dataset.picoeuk_moana.values)==False)
        
        # Get nearest lat-lon then group and average
        fdate = flist[0].split('/')[-1].split('.')[1]
        fdate = np.datetime64(fdate[:4]+'-'+fdate[4:6]+'-'+fdate[6:8])
        fdate = np.array([fdate]*good_inds[0].shape[0])
        labels = GetClosestCluster(LO,LA, total_labels, dataset.latitude.values[good_inds].flatten(), 
                                   dataset.longitude.values[good_inds].flatten(), fdate)
        # Assing labels
        all_labels[good_inds] = labels
    
        # Compute statistics
        for ci in np.arange(optimum_k):
            # For each cluster..find points that have that flag
            inds = np.where(all_labels==ci)
    
            # If this cluster is present
            if inds[0].shape[0]> 0:
    
                # Get cell counts 
                for pi in np.arange(len(pcc_list)):
                    
                    slice_sum = np.nansum(dataset[pcc_list[pi]].values[inds])
                    slice_sum2 = np.nansum(dataset[pcc_list[pi]].values[inds]**2)
                    slice_size = inds[0].shape[0]
    
                    # running sum
                    moana_results[ci,pi, 0] = moana_results[ci,pi, 0] + slice_sum
    
                    # running count
                    moana_results[ci,pi, 1] = moana_results[ci,pi, 1] + slice_size
    
                    # variance
                    moana_results[ci,pi, 2] = moana_results[ci,pi, 2] + slice_sum2
    
    n = moana_results[:,:,1]
    moana_mean = moana_results[:,:,0]/n
    moana_variance = ((moana_results[:,:,2] / n - moana_mean ** 2) * n / (n - 1))**(1/2)

    return moana_mean, moana_variance
