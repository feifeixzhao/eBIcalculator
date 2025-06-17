"""
Description: Will pull out annual averages from the WBM data for a list of coordinates.
Usage: This will require you to reach out to Sagy Cohen for the netCDF files with the WBM model output.
"""
import glob
import os
import re
import math
import glob

import xarray as xr
import netCDF4 as nc
import numpy as np
import pandas
from matplotlib import pyplot as plt
from scipy import spatial
from scipy.optimize import curve_fit
import rasterio


def func(x, a, b, c):
    return a * np.exp(-b * x) + c


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def findSlope(x, y, ds):
    image = ds.read(1)
    slopes = []
    pos = [
        (x, y),
    ]
    for (w, z) in pos:
        si = ds.index(w, z)
        slopes.append(image[si])
    return np.median(slopes)


def getRiverData(x, y, year_dict, name):
    years = sorted(year_dict.keys())
    data = {
        'years': [],
        'vals': [],
    }
    for year in years:
        print(year)
        nc_file = year_dict[year].replace('\\', '/')
        path = nc_file

        ds = rasterio.open(path)
        py, px = ds.index(x, y)
        window = rasterio.windows.Window(
            px - 1//2, 
            py - 1//2, 1, 1
        )
        pixel = ds.read(window=window)[0, 0, 0]
        data['years'].append(year)
        data['vals'].append(pixel)
    return pandas.DataFrame(data=data) 


def getLatLonIndex(Qds, xy):
    # Longitude index
    longitude = Qds['longitude'][:].data
    loni = np.argmin(np.abs(longitude - xy[0]))
    # Latitude index
    latitude = Qds['latitude'][:].data
    lati = np.argmin(np.abs(latitude - xy[1]))
    return [lati, loni]


def getYearDf(Qds, Qsds, xy, year):
    # Get discharge data
    monthlyQ = Qds['discharge'][:].data[:, xy[0], xy[1]]
    monthlyQs = Qsds['SedimentFlux'][:].data[:, xy[0], xy[1]]
    # Construct dataframe
    months = [i + 1 for i in range(len(monthlyQ))]
    return pandas.DataFrame(data={
        'year': [year for _ in months],
        'month': months,
        'Q': monthlyQ,
        'Qs': monthlyQs,
    })


# Define the base directory for the WBM data (Windows compatible)
base_dir = r"C:\Users\Feifei\Box\WBMsed"

# WBM paths updated for Windows
q_root = os.path.join(base_dir, "Discharge", "Annual", "*")
bedload_root = os.path.join(base_dir, "BedloadFlux", "*")
suspended_bed_root = os.path.join(base_dir, "SuspendedBedFlux", "*")
suspended_root = os.path.join(base_dir, "SedimentFlux", "Annual", "*")

q_fps = glob.glob(q_root)
bed_fps = glob.glob(bedload_root)
sus_bed_fps = glob.glob(suspended_bed_root)
sus_fps = glob.glob(suspended_root)

# Get all the file paths by year
q_years = {}
for fp in q_fps:
    year = fp.split(os.sep)[-1].split('.')[0][-4:]
    q_years[year] = fp

bed_years = {}
for fp in bed_fps:
    year = fp.split(os.sep)[-1].split('.')[0][-4:]
    bed_years[year] = fp

sus_bed_years = {}
for fp in sus_bed_fps:
    year = fp.split(os.sep)[-1].split('.')[0][-4:]
    sus_bed_years[year] = fp

sus_years = {}
for fp in sus_fps:
    year = fp.split(os.sep)[-1].split('.')[0][-4:]
    sus_years[year] = fp

# Read in the coordinate CSV from the specified Windows path and select only the relevant columns
in_path = r"C:\Users\Feifei\Box\BR_remote_sensing\eBI_Zhao.csv"
to_run = pandas.read_csv(in_path)
# Select and rename columns to match the expected column names
to_run = to_run[['River_Station', 'Latitude (deg)', 'Longitude (deg)']]
to_run = to_run.rename(columns={"River_Station": "Name", "Latitude (deg)": "Lat", "Longitude (deg)": "Long"})

combined = None
for j, row in to_run.iterrows():
    print(row['Name'])
    river = row['Name']
    lat = row['Lat']
    lon = row['Long']

    discharge_df = getRiverData(lon, lat, q_years, 'discharge')
    bedload_df = getRiverData(lon, lat, bed_years, 'BedloadFlux')
    sus_bed_df = getRiverData(lon, lat, sus_bed_years, 'SuspendedBedFlux')
    sus_df = getRiverData(lon, lat, sus_years, 'SedimentFlux')

    df = discharge_df[['years']]
    df['Q'] = discharge_df['vals']
    df['BedQs'] = bedload_df['vals']
    df['SusBedQs'] = sus_bed_df['vals']
    df['SusQs'] = sus_df['vals']
    df['Name'] = river
    df['Location'] = river[:-1]
    df['Lat'] = lat
    df['Lon'] = lon 

    if combined is None:
        combined = df
    else:
        combined = pandas.concat([combined, df.reset_index(drop=True)])

    # Define the output base directory
    output_base = r"C:\Users\Feifei\Box\BR_remote_sensing"

    # In the loop, update the output paths as follows:
    opath = os.path.join(output_base, f'{river}_wbm_data.csv')
    #df.to_csv(opath, index=False)

    opath = os.path.join(output_base, 'wbm_data.csv')
    combined.to_csv(opath, index=False)

