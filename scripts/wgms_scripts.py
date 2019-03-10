"""
WGMS Project Module
Author: Ann Windnagel
Date: 3/3/2019

This module contains functions that help to process RGI and GLIMS data. 
It currently contains 3 functions:
* open_rgi_region: opens RGI data
* pip: Determine if a glacier outline is within a larger glacier region
* split_glims: Split the glims data into the 19 regions

"""

import geopandas as gpd



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
                             "04_rgi60_ArcticCanadaNorth/04_rgi60_ArcticCanadaNorth.shp",
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
                             "18_rgi60_NewZealand/18_rgi60_NewZealand.shp"
                             "19_rgi60_AntarcticSubantarctic/19_rgi60_AntarcticSubantarctic.shp"]

        # Open file 
        rgi_region_df = gpd.read_file(root_data_dir + region_file_names[region_no-1])
        print(region_file_names[region_no-1])
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