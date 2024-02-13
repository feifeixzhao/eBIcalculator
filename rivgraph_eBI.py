from rivgraph.classes import river
from rivgraph import im_utils as iu
import matplotlib.pyplot as plt
from rivgraph.classes import rivnetwork
from rivgraph import mask_to_graph as m2g
from rivgraph.rivers import river_utils as ru
import os
from datetime import datetime
import csv
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Polygon

# Function to compute mesh for a given mask and save meshlines - this only needs to be done once per river
def compute_mesh_and_save(mask_path, name, results_folder):
    River = river(name, mask_path, results_folder, exit_sides='WE', verbose=True)
    River.compute_mesh(buf_halfwidth=5000, smoothing=0.5, grid_spacing=500)
    River.to_geovectors('centerline', ftype='json')
    River.to_geovectors('mesh', ftype='json')

# Function to compute links for a given mask and save them in date-based subfolders
def compute_links_and_save(mask_path, name, parent_results_folder):
    # Extract date (or numbers) from the mask name
    date_numbers = [char for char in mask_path if char.isdigit()]
    date_folder = ''.join(date_numbers)

    # Create a folder to save links for each mask based on the date
    mask_links_folder = os.path.join(parent_results_folder, date_folder, f'links_{name}')
    os.makedirs(mask_links_folder, exist_ok=True)

    # Initialize river object
    River = river(name, mask_path, mask_links_folder, exit_sides='WE', verbose=True)
    
    # Fill small holes in the mask
    River.Imask = iu.fill_holes(River.Imask, maxholesize=5)

    # Compute network, prune, and compute link width and length
    River.compute_network()
    River.prune_network()
    River.compute_link_width_and_length()

    # Save links for the current mask
    River.to_geovectors('network', ftype='json')  

# Function to calculate eBI_array for a given mask using saved meshlines and links
def calculate_eBI(meshlines, links):
    [eBI, BI] = ru.compute_eBI(meshlines, links, method='local')
    eBI_array = np.array([eBI])
    eBI_array = eBI_array[eBI_array != 0]
    return eBI_array

# Folder containing masks
mask_folder = '/Users/Feifei/GEE_watermasks-master/ebi/Ob_Phominskoje/output/mask/'

# Results will be saved with this name
name = 'Ob'

# Parent folder to organize results based on the date
results_folder = '/Users/Feifei/GEE_watermasks-master/ebi/Ob_Phominskoje/rivgraph/'

# Define the path to the first image (or whatever image you want to find mesh)
first_mask_path = os.path.join(mask_folder, 'Ob_2017_05-01_09-01_mask.tif')

# Compute mesh for the first mask and save meshlines 
compute_mesh_and_save(first_mask_path, name, results_folder)

# Get the paths to meshlines and links for the first mask
meshlines_path = os.path.join(results_folder, f'{name}_meshlines.json')

# Create a CSV file to store eBI_array for each mask
csv_filename = 'eBI_results.csv'
csv_filepath = os.path.join(results_folder, csv_filename)


# Loop through all masks in the folder
for mask_file in os.listdir(mask_folder):
    if mask_file.endswith('.tif'):
        mask_path = os.path.join(mask_folder, mask_file)

         # Get the paths to meshlines and links for the current mask
        date_numbers = [char for char in mask_path if char.isdigit()]
        date_folder = ''.join(date_numbers)
        meshlines_path = os.path.join(results_folder, f'{name}_meshlines.json')

        mask_links_folder = os.path.join(results_folder, date_folder, f'links_{name}')
        links_path = os.path.join(mask_links_folder, f'{name}_links.json')

        # Compute links for the current mask and save them in a date-based subfolder
        compute_links_and_save(mask_path, name, results_folder)

            # Calculate eBI_array for the current mask
        eBI_array = calculate_eBI(meshlines_path, links_path)

        # Append the results to the CSV file
        with open(csv_filepath, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([mask_file, *eBI_array])

centerline_pix, valley_centerline_widths = ru.mask_to_centerline(Brahm.Imask, Brahm.exit_sides)
self.max_valley_width_pixels = np.max(valley_centerline_widths)
self.centerline = gu.xy_to_coords(centerline_pix[:,0], centerline_pix[:,1], self.gt)
