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
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Compute links and save them for river masks.')
    parser.add_argument('--river_name', required=True, help='Full name of the river, e.g., Irrawaddy_Katha')
    parser.add_argument('--exit_sides', required=True, help='Exit sides for the river mask processing, e.g., EW')
    parser.add_argument('--timescale', required=True, choices=['annual', 'subannual'], 
                        help='Timescale for the mask folder: choose "annual" or "subannual"')
    args = parser.parse_args()
    return args

def compute_links_and_save(mask_path, name, parent_results_folder):
    # Ensure the 'links_and_nodes' folder exists in the parent_results_folder
    links_and_nodes_folder = os.path.join(parent_results_folder, 'links_and_nodes')
    os.makedirs(links_and_nodes_folder, exist_ok=True)

    # Extract date (or numbers) from the mask name
    date_numbers = ''.join([char for char in mask_path if char.isdigit()])
    date_folder = ''.join(date_numbers)

    # Create a subfolder to save links for each mask based on the date inside the 'links_and_nodes' folder
    mask_links_folder = os.path.join(links_and_nodes_folder, date_folder, f'links_{name}')
    os.makedirs(mask_links_folder, exist_ok=True)

    # Initialize river object
    River = river(name, mask_path, mask_links_folder, exit_sides, verbose=True)
    
    # Fill small holes in the mask
    River.Imask = iu.fill_holes(River.Imask, maxholesize=5)
    River.Imask = iu.largest_blobs(River.Imask, nlargest=1, action='keep')

    # Compute network, prune, and compute link width and length
    River.compute_network()
    River.compute_link_width_and_length()

    # Save links for the current mask
    River.to_geovectors('network', ftype='json')
    
    return mask_links_folder  # Returns the path to the folder where the results are saved

def calculate_eBI(meshlines, links):
    [eBI, BI, wetted_width] = ru.compute_eBI(meshlines, links, method='local')
    eBI_array = np.array([eBI])
    eBI_array = eBI_array[eBI_array != 0]
    BI_array = np.array([BI])
    BI_array = BI_array[BI_array != 0]
    wetted_area = np.array([wetted_width])
    wetted_area = wetted_area[wetted_area != 0]
    return eBI_array, BI_array, wetted_area

def extract_info_from_mask_file(mask_file):
    parts = os.path.splitext(mask_file)[0].split('_')
    
    # Extract river name
    river_name = ''
    for part in parts:
        if not part.isdigit():
            river_name += part + '_'
        else:
            break
    river_name = river_name.rstrip('_')

    # Extract year
    year = ''
    for part in parts:
        if part.isdigit() and len(part) == 4:
            year = part
            break

    # Remove the year between month dates
    month_parts = []
    for part in parts:
        if part.isdigit() and len(part) == 2:
            month_parts.append(part)
    month_dates_with_underscores = '_'.join(month_parts)

    return river_name, year, month_dates_with_underscores


if __name__ == "__main__":
    args = parse_args()

    base_dir = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_results"

    # Extract 'name' from 'river_name' by taking the part before the first underscore
    name = args.river_name.split('_')[0]

    # Use the arguments to construct paths
    river_name = args.river_name
    exit_sides = args.exit_sides

    # Adjust mask_folder based on the 'timescale' argument
    if args.timescale == 'annual':
        mask_folder = os.path.join(base_dir, f"{river_name}\\output_annual\\{river_name}\\mask_cropped")
    else:  # 'subannual'
        mask_folder = os.path.join(base_dir, f"{river_name}\\output_subannual\\{river_name}\\mask_cropped")

    results_folder = os.path.join(base_dir, f"{river_name}\\rivgraph")

    # Append timescale to CSV file names
    csv_suffix = f"_{args.timescale}"
    csv_filename = f'eBI_results{csv_suffix}.csv'
    bi_csv_filename = f'BI_results{csv_suffix}.csv'
    wetted_width_csv_filename = f'wetted_area{csv_suffix}.csv'

    # Full paths for the CSV files
    csv_filepath = os.path.join(results_folder, csv_filename)
    bi_csv_filepath = os.path.join(results_folder, bi_csv_filename)
    wetted_width_csv_filepath = os.path.join(results_folder, wetted_width_csv_filename)

    # Check if the eBI results CSV file exists and remove it if it does
    if os.path.exists(csv_filepath):
        os.remove(csv_filepath)

    if os.path.exists(bi_csv_filepath):
        os.remove(bi_csv_filepath)

    if os.path.exists(wetted_width_csv_filepath):
        os.remove(wetted_width_csv_filepath)

    # Create links and nodes folder if it doesn't exist
    links_and_nodes_folder = os.path.join(results_folder, 'links_and_nodes')
    os.makedirs(links_and_nodes_folder, exist_ok=True)

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

            mask_links_folder = os.path.join(links_and_nodes_folder, date_folder, f'links_{name}')
            links_path = os.path.join(mask_links_folder, f'{name}_links.json')

            # Compute links for the current mask and save them in a date-based subfolder
            compute_links_and_save(mask_path, name, results_folder)

            # Extract river name, year, and month-dates from the mask file name
            river_name, year, month_dates = extract_info_from_mask_file(mask_file)

            # Calculate eBI_array for the current mask
            eBI_array, BI_array, wetted_area = calculate_eBI(meshlines_path, links_path)

            # Write results to CSV files
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

            with open(wetted_width_csv_filepath, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                if os.path.getsize(wetted_width_csv_filepath) == 0:
                    csvwriter.writerow(['River', 'Year', 'Month_range', 'wetted_width', 'Cross_section'])
                for i, val in enumerate(wetted_area):
                    csvwriter.writerow([river_name, year, month_dates, val, 1+i])

print("eBI, BI, and wetted area are calculated.")

