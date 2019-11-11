"""
WGMS Project Module
Author: Ann Windnagel
Date: 3/3/2019

This module contains functions that help to process RGI and GLIMS data. 
It currently contains 4 functions:
* open_rgi_region: Opens RGI data file for a particular region
* open_clean_glims: Opens a cleaned GLIMS data file for a particular region
* pip: Determine if a glacier outline is within a larger glacier region
* split_glims: Split the glims data into the 19 regions
* clean_glims: Clean the glims regional files
* print_10_largest_glims: Prints the ten largest glaciers for a particular region for GLIMS
* print_10_largest_rgi: Prints the ten largest glaciers for a particular region for RGI
* multi_temporal_glims: Finds all the dates that the largest 3 glaciers have measurements 
  for each of the 19 regions from GLIMS.
* find_glacier_all_glims: Extract the data rows for a particular glacier from the full GLIMS database, 
  which contains all temporal measurements.
* find_glacier_clean_glims: Extract the data rows for a particular glacier from the cleaned 
  GLIMS database, which contains only the latest measurements. 
* ten_largest: Finds the 10 largest glaciers in a region and saves them to a csv file
* save_3_largest: Saves the 3 largest glacier outlines in a region to a shapefile
* explode_glaciers: merges all glaciers that touch each other
* ten_largest_icecaps: Finds the 10 largest ice caps in a region and saves them to a csv file


"""

import geopandas as gpd
import pandas as pd
import os
import fiona
from shapely.ops import cascaded_union
from shapely.geometry import shape, mapping


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
        # List of RGI region shapefile names
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
        #print(region_file_names[region_no-1])
        rgi_region_df = gpd.read_file(root_data_dir + region_file_names[region_no-1])
    else:
        rgi_region_df = "-999"
        print("Specified region does not exist.")
    
    return rgi_region_df


def open_clean_glims(region_no):
    '''
    Opens cleaned GLIMS shapefile for one of 19 glacial regions

    Parameters
    ----------
    region_no : The region number as an integer. Accepted values are 1 through 19.

    Returns
    ----------
    glims_region_df: Returns a geopandas dataframe of the shapefile for given region.
    '''
    
    if region_no >= 1 and region_no <=19:        
        
        # Open file
        glims_fp = "data/glims/processed/cleaned/glims_region_" + str(region_no) + "_cleaned.shp" 
        glims_region_df = gpd.read_file(glims_fp)
        
    else:
        glims_region_df = "-999"
        print("Specified region does not exist.")
    
    return glims_region_df    



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
    all_regions : Geodataframe containing outlines of the 19 glacier regions.
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
    
    print(region.RGI_CODE[0])
    
    glims_region.insert(0, 'region_no', region.RGI_CODE[0])

    # Save regional dataframe to shapefile
    glims_region.to_file(driver='ESRI Shapefile', filename=fp)
    
    return

def clean_glims(region_glims, fp):
    """
    Clean each GLIMS regional file: pull out only the glacier boundaries, remove extra columns, find latest date.
    Then save the cleaned outlines to its own shapefile for later use.

    Parameters
    ----------
    region_glims : Geodataframe containing polygons for one region of GLIMS data
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

def print_10_largest_glims(region_no, do_print=None):
    """
    Opens and prints the list of 10 largest glaciers for a specified region for GLIMS and
    returns the data as a pandas dataframe.

    Parameters
    ----------
    region_no : The region number as an integer. Accepted values are 1 through 19.
    do_print : String, if set to "false", will not print. Default is to print.

    Returns
    -------
    glims_largest : A pandas dataframe with a list of the 10 largest glaciers for the specified region
    """
    
    # Check do_print. If not set, set to true
    do_print = do_print or "true"
    
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
    if do_print != "false":
        print('GLIMS 10 Largest glaciers and their size for Region ' + str(region_no) + ' - ' + region_names[region_no-1] + ':')
        print('')
        print('      Glacier ID               Area (km^2)      Glacier Name       Date of Measurement')
        print(glims_largest.to_string(header=False, index=False, col_space=20))
    
    return glims_largest

def print_10_largest_rgi(region_no, do_print=None):
    """
    Opens and prints the list of 10 largest glaciers for a specified region for RGI and
    returns the data as a pandas dataframe.

    Parameters
    ----------
    region_no : The region number as an integer. Accepted values are 1 through 19.
    do_print : String, if set to "false", will not print. Default is to print.

    Returns
    -------
    rgi_largest : A pandas dataframe with a list of the 10 largest glaciers for the specified region
    """

    # Check do_print. If not set, set to true
    do_print = do_print or "true"
    
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
    
    if do_print != "false":
        print('RGI 10 Largest glaciers and their size for Region ' + str(region_no) + ' - ' + region_names[region_no-1] + ':')
        print('')
        print('      Glacier ID               Area (km^2)      Glacier Name       Date of Measurement')
        print(rgi_largest.to_string(header=False, index=False, col_space=20))
    
    return rgi_largest

def multi_temporal_glims(region_no, do_print=None):
    """
    Finds all the dates that the largest 3 glaciers have measurements for for each of the 19 regions from GLIMS.

    Parameters
    ----------
    region_no : The region number as an integer. Accepted values are 1 through 19.
    do_print : String, if set to "false", will not print. Default is to print.

    Returns
    -------
    glims_multi_temporal_largest : A pandas dataframe with a list of the 3 largest glaciers for the specified region
                                 along with all the different dates that they have measurements.
    """
    
    # Open GLIMS region shapefile
    glims_region_fp = "data/glims/processed/glims_region_" + str(region_no) + ".shp"
    glims_polygons = gpd.read_file(glims_region_fp)

    # Open and print GLIMS Region csv file with 10 largest glaciers
    glims_largest = print_10_largest_glims(region_no, do_print="false")
    
    # Find all the instances for when the top 3 largest glaciers occur
    largest_1 = glims_polygons[(glims_polygons['glac_id'] == glims_largest.glac_id[0]) &
                (glims_polygons['line_type'] == "glac_bound")]

    largest_2 = glims_polygons[(glims_polygons['glac_id'] == glims_largest.glac_id[1]) &
                (glims_polygons['line_type'] == "glac_bound")]


    largest_3 = glims_polygons[(glims_polygons['glac_id'] == glims_largest.glac_id[2]) &
                (glims_polygons['line_type'] == "glac_bound")]

    # Concantenate them all together
    glims_multi_temporal_largest = pd.concat([largest_1, largest_2, largest_3])
                              
    if do_print != "false":
        print(largest_1[['glac_name', 'glac_id', 'src_date', 'db_area']])
        print('')
        
        print(largest_2[['glac_name', 'glac_id', 'src_date', 'db_area']])
        print('')
        
        print(largest_3[['glac_name', 'glac_id', 'src_date', 'db_area']])
        print('')
    
    return glims_multi_temporal_largest

def find_glacier_all_glims(glims_id, region_no):
    """
    Extract the data rows for a particular glacier from the full GLIMS database, which contains all temporal
    measurements.

    Parameters
    ----------
    glims_id : String containing the GLIMS glacier id.
    region_no : The region number as an integer. Accepted values are 1 through 19. This number is required 
                to open the correct data file.

    Returns
    -------
    glims_data : A pandas dataframe with a the rows of data associated with the given glims id.
    """
    
    # Open the regional GLIMS file
    glims_glacier_data_fp = "data/glims/processed/glims_region_" + str(region_no) + ".shp"
    glims_glacier_data = gpd.read_file(glims_glacier_data_fp)
    
    # Find the glacier based on the GLIMS Id
    glims_glacier = glims_glacier_data[glims_glacier_data['glac_id']==glims_id]
    
    return glims_glacier

def find_glacier_clean_glims(glims_id, region_no):
    """
    Extract the data rows for a particular glacier from the cleaned GLIMS database, which contains only the latest
    measurements.

    Parameters
    ----------
    glims_id : String containing the GLIMS glacier id.
    region_no : The region number as an integer. Accepted values are 1 through 19. This number is required 
                to open the correct data file.

    Returns
    -------
    glims_data : A pandas dataframe with a the rows of data associated with the given glims id.
    """
    
    # Open the regional GLIMS file
    glims_glacier_data_fp = "data/glims/processed/cleaned/glims_region_" + str(region_no) + "_cleaned.shp"
    glims_glacier_data = gpd.read_file(glims_glacier_data_fp)
    
    # Find the glacier based on the GLIMS Id
    glims_glacier = glims_glacier_data[glims_glacier_data['glac_id']==glims_id]
    
    return glims_glacier

def ten_largest(data, region_no, source):
    '''
    Finds the 10 largest glaciers in a region and saves them to a csv file

    Parameters
    ----------
    data : Geodataframe containing all glacier polygons for a region
    region_no : Integer with the region number. Accepted values are 1 through 19.
    source :  String with the source of the glacier outlines. Accepted values are GLIMS or RGI

    Returns
    ----------
    nothing: Saves a csv file of the 10 largest glaciers for a region
    '''
    
    if source == 'GLIMS':
        # Find 10 largest
        ten_largest_df = data[['glac_id', 'db_area', 'glac_name', 'src_date']].nlargest(10, 'db_area')
        
        # Save to csv file if it doesn't already exist
        glims_largest_csv_fp = "data/glims/processed/largest/glims_region_" + str(region_no) + "_largest.csv"
        if os.path.exists(glims_largest_csv_fp) == False:
            print(region_no)
            ten_largest_df.to_csv(glims_largest_csv_fp, index=False)
        
    elif source == 'RGI':
        # Find 10 largest
        ten_largest_df = data[['GLIMSId', 'Area', 'Name', 'BgnDate']].nlargest(10, 'Area')
        
        # Save to csv file if it doesn't already exist
        rgi_largest_csv_fp = "data/rgi/processed/largest/rgi_region_" + str(region_no) + "_largest.csv"
        if os.path.exists(rgi_largest_csv_fp) == False:
            print(region_no)
            ten_largest_df.to_csv(rgi_largest_csv_fp, index=False)
        
    else:
        print("Incorrect source input")
    
    return

def save_3_largest(largest_1_df, largest_2_df, largest_3_df, region_no, source):
    '''
    Saves the 3 largest glacier outlines in a region to a shapefile

    Parameters
    ----------
    largest_1_df : Geodataframe containing the first largest glacier polygon for a region
    largest_2_df : Geodataframe containing the second largest glacier polygon for a region
    largest_3_df : Geodataframe containing the third largest glacier polygon for a region
    region_no : Integer with the region number. Accepted values are 1 through 19
    source :  String with the source of the glacier outlines. Accepted values are GLIMS or RGI

    Returns
    ----------
    nothing: Saves a shapefile 3 largest GLIMS glaciers for a region
    '''    
    
    # Set file path based on source selected
    if source == 'GLIMS':
        largest_3_fp = "data/glims/processed/largest/glims_region_" + str(region_no) + "_largest.shp"
    elif source == 'RGI':
        largest_3_fp = "data/rgi/processed/largest/rgi_region_" + str(region_no) + "_largest.shp"
    else:
        print("Incorrect source input")
        return
    
    # Check if the file already exists; if it does not, save file.
    if os.path.exists(largest_3_fp) == False:
        # Concatenate the 3 biggest into one dataframe
        largest_3 = gpd.GeoDataFrame(pd.concat([largest_1_df, largest_2_df, largest_3_df]))

        # Save 3 largest from specified region to shapefile
        largest_3.to_file(driver='ESRI Shapefile', filename=largest_3_fp)
    
    return

def explode_glaciers(region_no, source):
    '''
    Explodes (merges) all glacier polygons that touch one another into one polygon because these are part of a glacier catchment
    
    Parameters
    ----------
    region_no : Integer region number of the region with the polygons that need to be exploded, Accepted values are 1 through 19.
    source :  String with the source of the glacier outlines. Accepted values are GLIMS or RGI
    
    Returns : 
    nothing: Saves a file of exploded shapefiles
    '''
    if source == 'GLIMS':
        # Set up output filename
        output_fn = "data/glims/processed/ice-caps/exploded/exploded_" + str(region_no) + ".shp"
    
        # Check that the region hasn't already been processed
        if os.path.exists(output_fn) == False:
            print(str(source) + " " + str(region_no))
            filename = "data/glims/processed/cleaned/glims_region_" + str(region_no) + "_cleaned.shp"

            with fiona.open(filename, 'r') as ds_in:
                crs = ds_in.crs
                drv = ds_in.driver

                geoms = []
                for x in ds_in:
                    geom = shape(x["geometry"])
                    if not geom.is_valid:
                        geom = geom.buffer(0)

                    geoms.append(geom)

                dissolved = cascaded_union(geoms)

            schema = {
                "geometry": "Polygon",
                "properties": {"id": "int"}
            }

            with fiona.open(output_fn, 'w', driver=drv, schema=schema, crs=crs) as ds_dst:
                for i, g in enumerate(dissolved):
                    ds_dst.write({"geometry": mapping(g), "properties": {"id": i}})
        else:
            print(str(source) + " Region " + str(region_no) + " has already been processed")
            
    elif source == 'RGI':
        # Set up RGI output filename
        output_fn = "data/rgi/processed/ice-caps/exploded/exploded_" + str(region_no) + ".shp"
        
        # List of RGI region shapefile names
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
    
        # Check that the region hasn't already been processed
        if os.path.exists(output_fn) == False:
            print(str(source) + " " + str(region_no))
            filename = "data/rgi/raw/" + region_file_names[region_no-1]
            print(filename)

            with fiona.open(filename, 'r') as ds_in:
                crs = ds_in.crs
                drv = ds_in.driver

                geoms = []
                for x in ds_in:
                    geom = shape(x["geometry"])
                    if not geom.is_valid:
                        geom = geom.buffer(0)

                    geoms.append(geom)

                dissolved = cascaded_union(geoms)

            schema = {
                "geometry": "Polygon",
                "properties": {"id": "int"}
            }

            with fiona.open(output_fn, 'w', driver=drv, schema=schema, crs=crs) as ds_dst:
                for i, g in enumerate(dissolved):
                    ds_dst.write({"geometry": mapping(g), "properties": {"id": i}})
        else:
            print(str(source) + " Region " + str(region_no) + " has already been processed")
            
    else:
        print("Incorrect source input")
            
    return

def ten_largest_icecaps(data, region_no, source):
    '''
    This funiton is still TBD. This is just a copy of the ten_largest function at the moment.
    Finds the 10 largest ice caps in a region and saves them to a csv file

    Parameters
    ----------
    data : Geodataframe containing all glacier polygons for a region
    region_no : Integer with the region number. Accepted values are 1 through 19.
    source :  String with the source of the glacier outlines. Accepted values are GLIMS or RGI

    Returns
    ----------
    nothing: Saves a csv file of the 10 largest ice caps for a region
    '''
    
    
    # Find 10 largest
    ten_largest_ic_df = data[['glac_id', 'db_area', 'glac_name', 'src_date']].nlargest(10, 'db_area')
     
    # Save to csv file if it doesn't already exist
    glims_largest_csv_fp = "data/glims/processed/ice-caps/largest/glims_region_" + str(region_no) + "_largest.csv"
    if os.path.exists(glims_largest_csv_fp) == False:
        print(region_no)
        ten_largest_df.to_csv(glims_largest_csv_fp, index=False)
        
    return