# Global Assessment of Glaciers
This is a repository for a glacier statistics project with the World Glacier Monitoring Service (WGMS). The goal of the project is to determine global statistics about glaciers such as largest glaciers in the world, fastest retreating glaciers, and glaciers that have disappeared for the 19 recognized glacial regions of the world. The project uses two glacier databases for the analysis: Global Land Ice Measurements from Space (GLIMS) and the Randolf Glacier Inventory (RGI).

## Background
Glaciers are retreating at an alarming rate. Montana’s Glacier National Park had 150 glaciers in 1850; today only 25 remain and they are shrinking. Muir glacier in Alaska has retreated 31 miles since 1892 and is now only a fraction of its former grandeur measuring at only 11 miles long, today. 

Not only are glaciers a beautiful part of our landscape that are disappearing but in many parts of the world glaciers are a source of fresh water and energy through the use of the melt water. As these glaciers retreat, these nations will be out of water or need to find alternative forms of energy. Studying glaciers helps to inform our knowledge of climate change and helps water and energy resource managers plan for the future. Researchers have performed many regional studies of glaciers; however, global studies are scarce. Therefore, I am doing a global assessment of glaciers and glacial retreat to further our knowledge of these important natural resources on a worldwide scale. The outcome of the project will be an education and outreach blog post to help to inform people of the changes occurring in glaciers across the globe.

I'm doing this project in conjunction with the [World Glacier Monitoring Service](https://wgms.ch/) located at the University of Zurich. The WGMS compiles and disseminates standardized data on glacier fluctuations.

## Tools and Packages Used

* geopandas
* matplotlib
* earthpy
* wgms_scripts - This is a custom script that is available in this repository in the scripts directory.

## Data Used

* GLIMS: http://www.glims.org/download/glims_db_20190304.tgz
  * GLIMS (Global Land Ice Measurements from Space) is a project designed to monitor the world's glaciers primarily using data from optical satellite instruments. It provides glacial outlines at multi-temporal resolution for glaciers around the world as shapefiles.
* RGI: https://www.glims.org/RGI/rgi60_dl.html
  * The Randolph Glacier Inventory (RGI) is a globally complete inventory of glacier outlines. Production of the RGI was motivated
by the preparation of the Fifth Assessment Report of the Intergovernmental Panel on Climate Change. It provides glacial outlines for glaciers around the world as shapefiles. The RGI is intended to be a snapshot of the world’s glaciers as they were near the beginning of the 21st century.
* GTN-G Regions: http://www.gtn-g.ch/database/GlacReg_2017.zip
  * Glacier regions are useful for regional assessments of glacier change and other parameters. This dataset, provided by the Global Terrestrial Network for Glaciers (GTN-G), defines 19 first-order glacier regions. The GTN-G is the framework for the internationally coordinated monitoring of glaciers and ice caps in support of the United Nations Framework Convention on Climate Change (UNFCCC).

## Description of Files in this Repository

* README.md: This file. Describes the wgms-glacier-project repository.
* notebooks/explore-glims.ipynb: This is a notebook with test code to open up GLIMS data files, explore the dataframes, and plot some data. Use this to familiarize yourself with the GLIMS data. It is not required for processing of the data.
* notebooks/explore-rgi.ipynb: This is a notebook with test code to open up RGI data files, explore the dataframes, and plot some data. Use this to familiarize yourself with the RGI data. It is not required for processing of the data.
* notebooks/clean-gtng-region-shapefile.ipynb: This notebook cleans the GTN-G_glacier_regions_201707.shp shapefile. There are some extraneous regions in this shapefile and this code removes those. This notebook is required for processing of the data.
* notebooks/split-glims-into-gtng-regions.ipynb: This notebook splits the one large GLIMS shapefile into 19 different shapefiles based on the 19 GTNG Glacier Regions. This allows for the comparison of GLIMS to the RGI data which come separated into the 19 regions. This notebook is required for processing of the data.
* notebooks/clean-glims-regions.ipynb: This notebook cleans up the GLIMS data. The glacier outlines in the GLIMS database are multitemporal, so each glacier has many entries. For the analysis to find the largest glaciers in the world, need to go with the latest glacier entry. In addition, GLIMS also has outlines for debris cover and rock outcrops as well as the glacier outlines, so need to pull out only glacier outlines. This notebook is required for processing of the data.
* notebooks/compare-glims-rgi.ipynb: This notebook does a comparison of GLIMS and RGI data to determine the 10 largest glaciers in each of the 19 world glacier regions. This notebook is required for processing of the data.
* presentations/Global-analysis-of-glaciers.pptx: A PowerPoint presentation with results from this analysis.
* scripts/wgms_scripts.py: This module contains functions that help to process RGI and GLIMS data.
It currently contains 3 functions:
   * open_rgi_region: opens RGI data
   * pip: Determine if a glacier outline is within a larger glacier region
   * split_glims: Split the glims data into the 19 regions

## Analysis Workflow

To run these notebooks, you need to have the data listed in the "Data Used" section in the following directory structure:
* GLIMS: data/glims/raw/glims_download_20190304
* RGI: data/rgi/raw
* GTN-G Regions: data/gtn-g-glacier-regions

Notebooks need to be run in this order:
* clean-gtng-region-shapefile.ipynb
* split-glims-into-gtng-regions.ipynb
* clean-glims-regions.ipynb
* compare-glims-rgi.ipynb

## Example Usage

* Run clean-gtng-region-shapefile.ipynb. This will clean the raw GTN-G region shapefile and create a directory named "cleaned" under the gtn-g-glacier-regions directory with the cleaned shapefile (GTN-G_glacier_regions_201707_cleaned.shp).
* Run split-glims-into-gtng-regions.ipynb. This will split the large GLIMS shapefile into the 19 GTN-G regions and create a directory called "processed" under the glims directory with 19 shapefiles, one for each region (e.g. glims_region_1.shp).
* Run clean-glims-regions.ipynb. This will remove extraneous rows from each of the 19 glims regional shapefiles. It will create a directory named "cleaned" under the glims/processed directory with the 19 cleaned shapefiles (e.g. glims_region_1_cleaned.shp).
* Run compare-glims-rgi.ipynb. This will open each GLIMS and RGI regional shapefile and pull out the top 10 largest glaciers for each region from each database. These will be printed out in the notebook. Manual inspection of the notebook will be necessary to continue analysist to determine if the lists match and which glaciers are really largest.
