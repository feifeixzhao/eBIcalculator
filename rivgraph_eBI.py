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
import cv2

# Function to compute links for a given mask and save them in date-based subfolders
def compute_links_and_save(mask_path, name, parent_results_folder):
    # Extract date (or numbers) from the mask name
    date_numbers = ''.join([char for char in mask_path if char.isdigit()])
    date_folder = date_folder = ''.join(date_numbers)

    # Create a folder to save links for each mask based on the date
    mask_links_folder = os.path.join(parent_results_folder, date_folder, f'links_{name}')
    os.makedirs(mask_links_folder, exist_ok=True)

    # Initialize river object
    River = river(name, mask_path, mask_links_folder, exit_sides, verbose=True)
    
    # Fill small holes in the mask
    River.Imask = iu.fill_holes(River.Imask, maxholesize=5)

    # Compute network, prune, and compute link width and length
    River.compute_network()
    # River.prune_network()
    River.compute_link_width_and_length()

    # Save links for the current mask
    River.to_geovectors('network', ftype='json')  
    return mask_links_folder

# Function to calculate eBI_array for a given mask using saved meshlines and links
def calculate_eBI(meshlines, links):
    [eBI, BI] = ru.compute_eBI(meshlines, links, method='local')
    eBI_array = np.array([eBI])
    eBI_array = eBI_array[eBI_array != 0]
    BI_array = np.array([BI])
    BI_array = BI_array[BI_array != 0]
    return eBI_array, BI_array

# Function to extract river name, year, and month-dates from the mask file name
def extract_info_from_mask_file(mask_file):
    parts = os.path.splitext(mask_file)[0].split('_')
    river_name = '_'.join(parts[:-4]) 
    year_index = ''.join(filter(str.isdigit, mask_file)).find(parts[-4][:4])
    year = ''.join(filter(str.isdigit, mask_file))[:4]  # Extract the first four numeric characters as year
    month_dates = ''.join(filter(str.isdigit, mask_file))[4:]  # Extract all numeric characters after the year
    month_dates_with_underscores = '_'.join(month_dates[i:i+2] for i in range(0, len(month_dates), 2))
    return river_name, year, month_dates_with_underscores

# Folder containing masks
mask_folder = r"C:\Users\Feifei\PHD\Landsat_watermasks\ebi_results\Irrawaddy_Katha\output\Irrawaddy_Katha\mask"

# Results will be saved with this name
name = 'Irrawaddy'
exit_sides ='EW'

# Parent folder to organize results based on the date
results_folder = r"C:\Users\Feifei\PHD\Landsat_watermasks\ebi_results\Irrawaddy_Katha\rivgraph"

# Get the paths to meshlines and links for the first mask
meshlines_path = os.path.join(results_folder, f'{name}_meshlines.json')

# Create a CSV files
csv_filename = 'eBI_results.csv'
csv_filepath = os.path.join(results_folder, csv_filename)

bi_csv_filename = 'BI_results.csv'
bi_csv_filepath = os.path.join(results_folder, bi_csv_filename)

# Check if the eBI results CSV file exists and remove it if it does
if os.path.exists(csv_filepath):
    os.remove(csv_filepath)

if os.path.exists(bi_csv_filepath):
    os.remove(bi_csv_filepath)

# Loop through all masks in the folder
for mask_file in os.listdir(mask_folder):
    if mask_file.endswith('.tif'):
        mask_path = os.path.join(mask_folder, mask_file)

        # Use OpenCV to read the image
        mask_array = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)

        # Check if the mask is blank (all pixel values are zero)
        if np.all(mask_array == 0):
            print(f"Skipping blank mask: {mask_file}")
            continue

        # Get the paths to meshlines and links for the current mask
        date_numbers = [char for char in mask_path if char.isdigit()]
        date_folder = ''.join(date_numbers)
        meshlines_path = os.path.join(results_folder, f'{name}_meshlines.json')

        mask_links_folder = os.path.join(results_folder, date_folder, f'links_{name}')
        links_path = os.path.join(mask_links_folder, f'{name}_links.json')

        # Compute links for the current mask and save them in a date-based subfolder
        compute_links_and_save(mask_path, name, results_folder)


        # Extract river name, year, and month-dates from the mask file name
        river_name, year, month_dates = extract_info_from_mask_file(mask_file)


        # Calculate eBI_array for the current mask
        eBI_array, BI_array = calculate_eBI(meshlines_path, links_path)

        with open(csv_filepath, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            if os.path.getsize(csv_filepath) == 0:
                csvwriter.writerow(['River', 'Year', 'Month_range', 'eBI', 'Cross_section'])
            for i, val in enumerate(eBI_array):
                csvwriter.writerow([river_name, year, month_dates, val, 1+i])
        with open(bi_csv_filepath, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            if os.path.getsize(bi_csv_filepath) == 0:
                csvwriter.writerow(['River', 'Year', 'Month_range', 'BI', 'Cross_section'])
            for i, val in enumerate(BI_array):
                csvwriter.writerow([river_name, year, month_dates, val, 1+i])

print("eBI and BI are calculated.")






