"""
WGMS Project Module
Author: Ann Windnagel
Date: 3/3/2019

This module contains functions that help to process RGI and GLIMS data. 
It currently contains 4 functions:
* open_rgi_region: opens RGI data
* pip: Determine if a glacier outline is within a larger glacier region
* split_glims: Split the glims data into the 19 regions
* clean_glims: Clean the glims regional files

"""

import geopandas as gpd
import pandas as pd


def open_rgi_region(region_no):
    '''
    Opens RGI shapefile for one of 19 glacial regions

    Parameters
    ----------
    region_no : The region number as an integer. Accepted values are 1 through 19.

    Returns
    ----------
    rgi_region_df: Returns a geopandas dataframe of the shapefile for given region.
    '''

    # root data directory
    root_data_dir = "data/rgi/raw/"

    if region_no >= 1 and region_no <=19:        
        # List of region shapefile names
        region_file_names = ["01_rgi60_Alaska/01_rgi60_Alaska.shp", 
                             "02_rgi60_WesternCanadaUS/02_rgi60_WesternCanadaUS.shp",
                             "03_rgi60_ArcticCanadaNorth/03_rgi60_ArcticCanadaNorth.shp", 
                             "04_rgi60_ArcticCanadaSouth/04_rgi60_ArcticCanadaSouth.shp",
                             "05_rgi60_GreenlandPeriphery/05_rgi60_GreenlandPeriphery.shp",
                             "06_rgi60_Iceland/06_rgi60_Iceland.shp",
                             "07_rgi60_Svalbard/07_rgi60_Svalbard.shp",
                             "08_rgi60_Scandinavia/08_rgi60_Scandinavia.shp",
                             "09_rgi60_RussianArctic/09_rgi60_RussianArctic.shp",
                             "10_rgi60_NorthAsia/10_rgi60_NorthAsia.shp",
                             "11_rgi60_CentralEurope/11_rgi60_CentralEurope.shp",
                             "12_rgi60_CaucasusMiddleEast/12_rgi60_CaucasusMiddleEast.shp",
                             "13_rgi60_CentralAsia/13_rgi60_CentralAsia.shp",
                             "14_rgi60_SouthAsiaWest/14_rgi60_SouthAsiaWest.shp",
                             "15_rgi60_SouthAsiaEast/15_rgi60_SouthAsiaEast.shp",
                             "16_rgi60_LowLatitudes/16_rgi60_LowLatitudes.shp",
                             "17_rgi60_SouthernAndes/17_rgi60_SouthernAndes.shp",
                             "18_rgi60_NewZealand/18_rgi60_NewZealand.shp",
                             "19_rgi60_AntarcticSubantarctic/19_rgi60_AntarcticSubantarctic.shp"]

        # Open file 
        print(region_file_names[region_no-1])
        rgi_region_df = gpd.read_file(root_data_dir + region_file_names[region_no-1])
    else:
        rgi_region_df = "-999"
        print("Specified region does not exist.")
    
    return rgi_region_df



def pip(polygon1, polygon2):
    """
    Determines if a polygon is within another polygon (pip - polygon in polygon)
    
    Parameters
    ----------
    polygon1 : A list of polygons in a geopandas dataframe to be tested if they are within polygon2.
    
    polygon2 : The polygon (in a geopandas dataframe) for which you want to test if polygon1 lies within it.
    
    Returns
    -------
    pip_mask : Returns a Series of dtype('bool') with value True for each polygon1 geometry that is within polygon2.
    """
    
    # Check if the list of polygons in polygon1 is within polygon2. Do a buffer on polygon1 incase
    # there are any invalid polygons
    pip_mask = polygon1.buffer(0).within(polygon2.loc[0, 'geometry'])
    
    return pip_mask



def split_glims(data, all_regions, region_name, fp):
    """
    Determines which glacier outlines, from the large GLIMS data file, belong to the specified region.
    Then saves the outlines that reside in that region to its own shapefile for later use.

    Parameters
    ----------
    data : Geodataframe containing polygons of all the GLIMS data
    regions : Geodataframe containing a single polygon of the region you want to check the GLIMS data against.
    region_name : String containing the name of the region
    fp : String containing the file path to the location where the region shapefile should be saved.

    Returns
    -------
    Nothing. Saves the outlines that reside in the specified region to its own shapefile.
    """
    
    # Select specified region from the regions dataframe and reset index to zero so that it works in pip
    region = all_regions[all_regions.FULL_NAME == region_name]
    region.reset_index(drop=True, inplace=True)
    
    # Determine which GLIMS outlines reside in specified region
    pip_mask = pip(data, region)

    # Pass pip_mask into data to get the ones that are in the specified region
    glims_region = data.loc[pip_mask]

    # Save regional dataframe to shapefile
    glims_region.to_file(driver='ESRI Shapefile', filename=fp)
    
    return

def clean_glims(region_glims, fp):
    """
    Clean each GLIMS regional file: pull out only the glacier boundaries, remove extra columns, find latest date.
    Then save the cleaned outlines to its own shapefile for later use.

    Parameters
    ----------
    region_glims : Geodataframe containing polygons for one regions of GLIMS data
    fp : String containing the file path to the location where the region shapefile should be saved.

    Returns
    -------
    Nothing. Saves the cleaned outlines to its own shapefile.
    """
    
    # Extract the glacier outlines: line_type = glac_bound
    glac_bounds = region_glims[region_glims['line_type']=='glac_bound']
    
    # Remove columns the are unneeded
    glac_bounds_trimmed = glac_bounds.drop(
                          ['line_type', 'anlys_id', 'anlys_time', 'rec_status', 'wgms_id', 
                          'local_id', 'glac_stat', 'subm_id', 'release_dt', 'proc_desc', 'rc_id', 
                          'geog_area', 'chief_affl', 'loc_unc_x', 'loc_unc_y', 'glob_unc_x', 
                          'glob_unc_y', 'submitters', 'analysts'], axis=1)
    
    # Find the unique glaciers in region 1 by glac_id
    unique_glaciers = glac_bounds_trimmed.glac_id.unique()
    
    # Find the latest date for each unique glacier and create a new dataframe with just those rows
    for counter, unique in enumerate(unique_glaciers):
        glacier = glac_bounds_trimmed[glac_bounds_trimmed['glac_id'] == unique]
        glacier_latest_date = glacier['src_date'].max()
        if counter == 0:
            # Create first instance of glacier_latest_df so that we can append to it later
            glacier_latest_df = glacier[glacier['src_date'] == glacier_latest_date]
        else:
            # Append the other rows to glacier_latest_df
            glacier_latest_df_part = glacier[glacier['src_date'] == glacier_latest_date]
            glacier_latest_df = glacier_latest_df.append(glacier_latest_df_part)
            
    # Save cleaned dataframe to a shapefile
    glacier_latest_df.to_file(driver='ESRI Shapefile', filename=fp)
    
    return

def print_10_largest_glims(region_no):
    """
    Opens and prints the list of 10 largest glaciers for a specified region for GLIMS and
    returns the data as a pandas dataframe.

    Parameters
    ----------
    region_no : The region number as an integer. Accepted values are 1 through 19.

    Returns
    -------
    glims_largest : A pandas dataframe with a list of the 10 largest glaciers for the specified region
    """
    
    # Create a list with all the region names
    region_names = ["Alaska", "Western Canada and USA",
                    "Arctic Canada, North", "Arctic Canada, South",
                    "Greenland Periphery", "Iceland", "Svalbard and Jan Mayen",
                    "Scandinavia", "Russian Arctic", "Asia, North", "Central Europe",
                    "Caucasus and Middle East", "Asia, Central", "Asia, South West",
                    "Asia, South East", "Low Latitudes", "Southern Andes", "New Zealand", 
                    "Antarctic and Subantarctic"]
    
    # Open GLIMS csv file for specified region with 10 largest glaciers
    glims_largest_fp = "data/glims/processed/largest/glims_region_" + str(region_no) + "_largest.csv"
    glims_largest = pd.read_csv(glims_largest_fp)
    print('GLIMS 10 Largest glaciers and their size for Region ' + str(region_no) + ' - ' + region_names[region_no-1] + ':')
    print('')
    print('      Glacier ID               Area (km^2)      Glacier Name       Date of Measurement')
    print(glims_largest.to_string(header=False, index=False, col_space=20))
    
    return glims_largest

def print_10_largest_rgi(region_no):
    """
    Opens and prints the list of 10 largest glaciers for a specified region for RGI and
    returns the data as a pandas dataframe.

    Parameters
    ----------
    region_no : The region number as an integer. Accepted values are 1 through 19.

    Returns
    -------
    rgi_largest : A pandas dataframe with a list of the 10 largest glaciers for the specified region
    """
    
    # Create a list with all the region names
    region_names = ["Alaska", "Western Canada and USA",
                    "Arctic Canada, North", "Arctic Canada, South",
                    "Greenland Periphery", "Iceland", "Svalbard and Jan Mayen",
                    "Scandinavia", "Russian Arctic", "Asia, North", "Central Europe",
                    "Caucasus and Middle East", "Asia, Central", "Asia, South West",
                    "Asia, South East", "Low Latitudes", "Southern Andes", "New Zealand", 
                    "Antarctic and Subantarctic"]
    
    # Open RGI csv file for specified region with 10 largest glaciers
    rgi_largest_fp = "data/rgi/processed/largest/rgi_region_" + str(region_no) + "_largest.csv"
    rgi_largest = pd.read_csv(rgi_largest_fp)
    print('RGI 10 Largest glaciers and their size for Region ' + str(region_no) + ' - ' + region_names[region_no-1] + ':')
    print('')
    print('      Glacier ID               Area (km^2)      Glacier Name       Date of Measurement')
    print(rgi_largest.to_string(header=False, index=False, col_space=20))
    
    return rgi_largest