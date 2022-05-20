# Global Assessment of Largest Glaciers
This is a repository for a glacier statistics project with the World Glacier Monitoring Service (WGMS). The goal of the project is to determine global statistics about glaciers such as largest glaciers in the 19 recognized glacial regions of the world as defined by the Global Terrestrial Network for Glaciers (GTN-G). The project uses two glacier databases for the analysis: Global Land Ice Measurements from Space (GLIMS) and the Randolf Glacier Inventory (RGI).

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

* GLIMS: glims_db_20190304.zip from https://doi.org/10.7265/N5V98602
  * GLIMS (Global Land Ice Measurements from Space) is a project designed to monitor the world's glaciers primarily using data from optical satellite instruments. It provides glacial outlines at multi-temporal resolution for glaciers around the world as shapefiles.
* RGI: https://doi.org/10.7265/4m1f-gd79
  * The Randolph Glacier Inventory (RGI) is a globally complete inventory of glacier outlines. Production of the RGI was motivated
by the preparation of the Fifth Assessment Report of the Intergovernmental Panel on Climate Change. It provides glacial outlines for glaciers around the world as shapefiles. The RGI is intended to be a snapshot of the world’s glaciers as they were near the beginning of the 21st century.
* GTN-G Regions: GlacReg_2017.zip from http://dx.doi.org/10.5904/gtng-glacreg-2017-07
  * Glacier regions are useful for regional assessments of glacier change and other parameters. This dataset, provided by the Global Terrestrial Network for Glaciers (GTN-G), defines 19 first-order glacier regions. The GTN-G is the framework for the internationally coordinated monitoring of glaciers and ice caps in support of the United Nations Framework Convention on Climate Change (UNFCCC).

## Description of Files in this Repository
Below is a list of the files that reside in this repo.

* **README.md**: This file. Describes the wgms-glacier-project repository.
* **notebooks/0-explore-glims.ipynb**: This is a notebook with test code to open up GLIMS data files, explore the dataframes, and plot some data. Use this to familiarize yourself with the GLIMS data. It is not required for processing of the data.
* **notebooks/0-explore-rgi.ipynb**: This is a notebook with test code to open up RGI data files, explore the dataframes, and plot some data. Use this to familiarize yourself with the RGI data. It is not required for processing of the data.
* **notebooks/1-clean-gtng.ipynb**: This notebook cleans the GTN-G_glacier_regions_201707.shp shapefile. There are some extraneous regions in this shapefile and this code removes those. Required for processing.
* **notebooks/2-split-glims.ipynb**: This notebook splits the one large GLIMS shapefile into 19 different shapefiles based on the 19 GTN-G Glacier Regions. This allows for the comparison of GLIMS to the RGI data which come separated into the 19 regions. Required for processing.
* **notebooks/3-clean-glims.ipynb**: This notebook cleans up the GLIMS data. The glacier outlines in the GLIMS database are multitemporal, so each glacier has many entries. For the analysis to find the largest glaciers in the world, need to go with the latest glacier entry. In addition, GLIMS also has outlines for debris cover and rock outcrops as well as the glacier outlines, so need to pull out only glacier outlines. Required for processing.
* **notebooks/3-clean-rgi.ipynb**: This notebook cleans RGI data. Specifically, the region 5 data where I must filter out glaciers with a connectivity of 2. Required for processing.
* **notebooks/4-compare-glims-rgi.ipynb**: This notebook does a comparison of GLIMS and RGI data to determine the 10 largest glaciers in each of the 19 world glacier regions. Required for processing.
* **notebooks/5-explode-glaciers.ipynb**: This notebook explodes (merges) all glacier polygons that are touching to turn them into one polygon to create a glacier complex. Required for processing.
* **notebooks/6-ice-cap-size.ipynb**: This notebook reads the exploded data files and calculates the area of the glacier complexes. Required for processing.
* **notebooks/7-analyze-region-\***: These notebooks do the final analysis of each of the 19 regions. They are required for processing but can be run in any order with the exception of 7-analyze-region-19-antarctic-and-subantarctic-preprocess.ipynb, which must be run before 7-analyze-region-19-antarctic-and-subantarctic.ipynb.
* **notebooks/8-summarize-results.iypnb**: This notebook reads the results from each of the finalized shapefiles and then summarizes and writes the results to CSV files for easy reference.
* **presentations/largest-glacier-presentation.ipynb**: This notebook was a homework assignment for GEOG 5663 presented in April 2019. It no longer contains the most current analysis. For information on the latest results, see the Results seciton below.
* **presentations/largest-glaciers-blog-post.ipynb**: This notebook was a homework assignment for GEOG 5663 presented in February 2019. It contains a short blog post of the findings of this analysis at that time. It no longer contains the most current analysis. For information on the latest results, see the Results seciton below.
* **presentations/Global-analysis-of-glaciers.pptx**: A PowerPoint presentation that was a homework assignment for GEOG 5663 presented in April 2019. It no longer contains the most current analysis. For information on the latest results, see the Results seciton below.
* **scripts/wgms_scripts.py**: This module contains functions that help to process RGI and GLIMS data.

## Results
The reults from this analysis are provided in shapefiles availabe from https://doi.org/10.7265/0k6h-yn09

## Analysis Workflow

To run these notebooks, you need to have the data listed in the "Data Used" section in the following directory structure:
* GLIMS: data/glims/raw/glims_download_20190304
* RGI: data/rgi/raw
* GTN-G Regions: data/gtn-g-glacier-regions

Notebooks need to be run in this order:
* 1-clean-gtng.ipynb
* 2-split-glims.ipynb
* 3-clean-glims.ipynb
* 4-compare-glims-rgi.ipynb
* 5-explode-glaciers.ipynb
* 6-ice-cap-size.ipynb
* 7-analyze-region-\* (these notebooks can be run in any order)
* 8-summarize-results
