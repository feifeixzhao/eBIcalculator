import os
import pandas as pd
import numpy as np
from datetime import datetime
import rasterio

# File paths
Galeazzi_file = r"C:\Users\Feifei\Box\BR_remote_sensing\Galeazzi_eBI.csv"
root_dir = r'C:\Users\Feifei\Box\BR_remote_sensing\ebi_results'
discharge_dir = r"C:\Users\Feifei\Box\BR_remote_sensing\water_discharge_data\processed"
full_data_path = r"C:\Users\Feifei\Box\BR_remote_sensing\channel_belt_stats\FullData_50_113023.csv"
mcleod_file = r"C:\Users\Feifei\Box\BR_remote_sensing\McLeod_Galeazzi_intermittency_new_forFeifei.csv"
koppen_tif = r"C:\Users\Feifei\Box\BR_remote_sensing\koppen_geiger_tif\1991_2020\koppen_geiger_0p00833333.tif"
legend_file = r"C:\Users\Feifei\Box\BR_remote_sensing\koppen_geiger_tif\legend.txt"
merged_piv_file = r"C:\Users\Feifei\Box\BR_remote_sensing\merged_PIV_eBI_TR.csv"  # New file

# Load datasets
river_df = pd.read_csv(Galeazzi_file)
full_data = pd.read_csv(full_data_path, usecols=['TR', 'River', 'CB/Aw'])
mcleod_df = pd.read_csv(mcleod_file)

# Rename 'River Station' to 'River' in the McLeod file for consistency
mcleod_df.rename(columns={'River Station': 'River'}, inplace=True)

# Extract climate zones from the Köppen-Geiger map
with rasterio.open(koppen_tif) as raster:
    def get_climate_zone(lat, lon):
        try:
            row, col = raster.index(lon, lat)
            value = raster.read(1)[row, col]
            return value
        except IndexError:
            return None

    river_df['Climate Zone Value'] = river_df.apply(
        lambda row: get_climate_zone(row['Latitude (deg)'], row['Longitude (deg)']), axis=1
    )

# Parse the legend file to create a mapping of climate zone values to names
climate_mapping = {}
with open(legend_file, 'r') as file:
    for line in file:
        if ':' in line:
            try:
                value, description = line.split(':')
                code = description.split()[0].strip()
                climate_mapping[int(value.strip())] = code
            except IndexError:
                continue

river_df['Climate Zone'] = river_df['Climate Zone Value'].map(climate_mapping)
river_df['Climate Zone'].fillna('Csb', inplace=True)

# Create a list to store combined DataFrames for each river folder
combined_statistics_dfs = []

# Helper functions
def parse_month_day(month_day_str):
    month, day = map(int, month_day_str.split('/'))
    return month, day

def is_within_range(date, start_str, end_str):
    start_month, start_day = parse_month_day(start_str)
    end_month, end_day = parse_month_day(end_str)
    date_month_day = (date.month, date.day)
    if (start_month, start_day) > (end_month, end_day):
        return date_month_day >= (start_month, start_day) or date_month_day <= (end_month, end_day)
    else:
        return (start_month, start_day) <= date_month_day <= (end_month, end_day)

# Iterate through each river folder
for river_folder in os.listdir(root_dir):
    river_path = os.path.join(root_dir, river_folder)
    if os.path.isdir(river_path):
        rivgraph_path = os.path.join(river_path, 'rivgraph')
        if os.path.isdir(rivgraph_path):
            # Subannual and annual file paths
            ebi_subannual_csv_path = os.path.join(rivgraph_path, 'eBI_results_subannual.csv')
            bi_subannual_csv_path = os.path.join(rivgraph_path, 'BI_results_subannual.csv')
            wetted_area_csv_path = os.path.join(rivgraph_path, 'wetted_area_subannual.csv')
            ebi_annual_csv_path = os.path.join(rivgraph_path, 'eBI_results_annual.csv')
            bi_annual_csv_path = os.path.join(rivgraph_path, 'BI_results_annual.csv')

            subannual_data = {}
            annual_data = {}

            # Subannual: Compute wetted area average if available.
            if os.path.exists(ebi_subannual_csv_path) and os.path.exists(bi_subannual_csv_path):
                ebi_df_sub = pd.read_csv(ebi_subannual_csv_path)
                bi_df_sub = pd.read_csv(bi_subannual_csv_path)
                if os.path.exists(wetted_area_csv_path):
                    wetted_area_df = pd.read_csv(wetted_area_csv_path)
                    wetted_area_avg_subannual = wetted_area_df['wetted_width'].mean()
                else:
                    wetted_area_avg_subannual = np.nan
                subannual_data['wetted_area_avg_subannual'] = wetted_area_avg_subannual

            # Annual statistics calculation
            if os.path.exists(ebi_annual_csv_path) and os.path.exists(bi_annual_csv_path):
                ebi_annual_df = pd.read_csv(ebi_annual_csv_path)
                bi_annual_df = pd.read_csv(bi_annual_csv_path)

                # --- eBI Statistics ---
                if not ebi_annual_df.empty and 'eBI' in ebi_annual_df.columns:
                    # Site stats (using all annual eBI values)
                    mean_ebi_site = ebi_annual_df['eBI'].mean()
                    median_ebi_site = ebi_annual_df['eBI'].median()
                    std_ebi_site = ebi_annual_df['eBI'].std()
                    cov_ebi_site = std_ebi_site / mean_ebi_site if mean_ebi_site != 0 else np.nan
                    ebi_95_site = np.percentile(ebi_annual_df['eBI'], 95)
                    ebi_5_site = np.percentile(ebi_annual_df['eBI'], 5)

                    # Reach stats: for each year, average across all cross sections; then aggregate across years.
                    ebi_reach_series = ebi_annual_df.groupby('Year')['eBI'].mean()
                    mean_ebi_reach = ebi_reach_series.mean()
                    median_ebi_reach = ebi_reach_series.median()
                    std_ebi_reach = ebi_reach_series.std()
                    ebi_95_reach = np.percentile(ebi_reach_series, 95) if not ebi_reach_series.empty else np.nan
                    ebi_5_reach = np.percentile(ebi_reach_series, 5) if not ebi_reach_series.empty else np.nan

                    # Cross_section stats: for each cross section, average across years; then aggregate across cross sections.
                    ebi_xsection_series = ebi_annual_df.groupby('Cross_section')['eBI'].mean()
                    mean_ebi_xsection = ebi_xsection_series.mean()
                    median_ebi_xsection = ebi_xsection_series.median()
                    std_ebi_xsection = ebi_xsection_series.std()
                    ebi_95_xsection = np.percentile(ebi_xsection_series, 95) if not ebi_xsection_series.empty else np.nan
                    ebi_5_xsection = np.percentile(ebi_xsection_series, 5) if not ebi_xsection_series.empty else np.nan
                else:
                    mean_ebi_site = median_ebi_site = std_ebi_site = cov_ebi_site = np.nan
                    ebi_95_site = ebi_5_site = np.nan
                    mean_ebi_reach = median_ebi_reach = std_ebi_reach = ebi_95_reach = ebi_5_reach = np.nan
                    mean_ebi_xsection = median_ebi_xsection = std_ebi_xsection = ebi_95_xsection = ebi_5_xsection = np.nan

                # --- BI Statistics ---
                if not bi_annual_df.empty and 'BI' in bi_annual_df.columns:
                    mean_bi_site = bi_annual_df['BI'].mean()
                    median_bi_site = bi_annual_df['BI'].median()
                    std_bi_site = bi_annual_df['BI'].std()
                    cov_bi_site = std_bi_site / mean_bi_site if mean_bi_site != 0 else np.nan
                    bi_95_site = np.percentile(bi_annual_df['BI'], 95)
                    bi_5_site = np.percentile(bi_annual_df['BI'], 5)

                    bi_reach_series = bi_annual_df.groupby('Year')['BI'].mean()
                    mean_bi_reach = bi_reach_series.mean()
                    median_bi_reach = bi_reach_series.median()
                    std_bi_reach = bi_reach_series.std()
                    bi_95_reach = np.percentile(bi_reach_series, 95) if not bi_reach_series.empty else np.nan
                    bi_5_reach = np.percentile(bi_reach_series, 5) if not bi_reach_series.empty else np.nan

                    bi_xsection_series = bi_annual_df.groupby('Cross_section')['BI'].mean()
                    mean_bi_xsection = bi_xsection_series.mean()
                    median_bi_xsection = bi_xsection_series.median()
                    std_bi_xsection = bi_xsection_series.std()
                    bi_95_xsection = np.percentile(bi_xsection_series, 95) if not bi_xsection_series.empty else np.nan
                    bi_5_xsection = np.percentile(bi_xsection_series, 5) if not bi_xsection_series.empty else np.nan
                else:
                    mean_bi_site = median_bi_site = std_bi_site = cov_bi_site = np.nan
                    bi_95_site = bi_5_site = np.nan
                    mean_bi_reach = median_bi_reach = std_bi_reach = bi_95_reach = bi_5_reach = np.nan
                    mean_bi_xsection = median_bi_xsection = std_bi_xsection = bi_95_xsection = bi_5_xsection = np.nan

                # --- eBI/BI Ratios ---
                if pd.notna(mean_ebi_site) and pd.notna(mean_bi_site) and mean_bi_site != 0:
                    eBI_BI_ratio_site = mean_ebi_site / mean_bi_site
                else:
                    eBI_BI_ratio_site = np.nan

                if not ebi_annual_df.empty and not bi_annual_df.empty and 'Cross_section' in ebi_annual_df.columns and 'Cross_section' in bi_annual_df.columns:
                    bi_xsection_series = bi_annual_df.groupby('Cross_section')['BI'].mean()
                    ratio_xsection = ebi_xsection_series / bi_xsection_series
                    eBI_BI_ratio_xsection = ratio_xsection.mean() if not ratio_xsection.empty else np.nan
                else:
                    eBI_BI_ratio_xsection = np.nan

                if not ebi_annual_df.empty and not bi_annual_df.empty:
                    ebi_reach_series = ebi_annual_df.groupby('Year')['eBI'].mean()
                    bi_reach_series = bi_annual_df.groupby('Year')['BI'].mean()
                    ratio_reach = ebi_reach_series / bi_reach_series
                    eBI_BI_ratio_reach = ratio_reach.mean() if not ratio_reach.empty else np.nan
                else:
                    eBI_BI_ratio_reach = np.nan

                annual_data.update({
                    # eBI site stats
                    'mean_ebi_site': mean_ebi_site,
                    'median_ebi_site': median_ebi_site,
                    'std_ebi_site': std_ebi_site,
                    'cov_ebi_site': cov_ebi_site,
                    '95_ebi_site': ebi_95_site,
                    '5_ebi_site': ebi_5_site,
                    # eBI reach stats
                    'mean_ebi_reach': mean_ebi_reach,
                    'median_ebi_reach': median_ebi_reach,
                    'std_ebi_reach': std_ebi_reach,
                    '95_ebi_reach': ebi_95_reach,
                    '5_ebi_reach': ebi_5_reach,
                    # eBI cross-section stats
                    'mean_ebi_xsection': mean_ebi_xsection,
                    'median_ebi_xsection': median_ebi_xsection,
                    'std_ebi_xsection': std_ebi_xsection,
                    '95_ebi_xsection': ebi_95_xsection,
                    '5_ebi_xsection': ebi_5_xsection,
                    # BI site stats
                    'mean_bi_site': mean_bi_site,
                    'median_bi_site': median_bi_site,
                    'std_bi_site': std_bi_site,
                    'cov_bi_site': cov_bi_site,
                    '95_bi_site': bi_95_site,
                    '5_bi_site': bi_5_site,
                    # BI reach stats
                    'mean_bi_reach': mean_bi_reach,
                    'median_bi_reach': median_bi_reach,
                    'std_bi_reach': std_bi_reach,
                    '95_bi_reach': bi_95_reach,
                    '5_bi_reach': bi_5_reach,
                    # BI cross-section stats
                    'mean_bi_xsection': mean_bi_xsection,
                    'median_bi_xsection': median_bi_xsection,
                    'std_bi_xsection': std_bi_xsection,
                    '95_bi_xsection': bi_95_xsection,
                    '5_bi_xsection': bi_5_xsection,
                    # eBI/BI ratios
                    'eBI_BI_ratio_site': eBI_BI_ratio_site,
                    'eBI_BI_ratio_xsection': eBI_BI_ratio_xsection,
                    'eBI_BI_ratio_reach': eBI_BI_ratio_reach
                })
            # End annual stats

            # Extract common variables from Galeazzi file
            galeazzi_row = river_df[river_df['River_Station'] == river_folder].iloc[0]
            qm, qmax, qmin = galeazzi_row[['Qm(m3/s)', 'Qmax(m3/s)', 'Qmin(m3/s)']]
            Width, classification, sinuosity, sp, Slope = galeazzi_row[['Width(m)', 'Classification', 'Sinuosity',
                                                                        'Stream Power (W/m) ', 'Slope (cm/km) ']]
            common_data = {
                'River': river_folder,
                'Width(m)': Width,
                'Stream Power (W/m) ': sp,
                'Classification': classification,
                'Sinuosity': sinuosity,
                'Slope (cm/km) ': Slope,
                'Qm': qm,
                'Qmax(m3/s)': qmax,
                'Qmin(m3/s)': qmin,
                'Climate Zone': galeazzi_row['Climate Zone']
            }

            # Get CB/Aw value from full_data (or compute it if not available)
            cb_aw_value = full_data[full_data['River'] == river_folder]['CB/Aw'].values
            if len(cb_aw_value) > 0 and not pd.isna(cb_aw_value[0]):
                cb_aw = cb_aw_value[0]
            else:
                output_annual_dir = os.path.join(root_dir, river_folder, 'output_annual', river_folder)
                cb_csv, mobility_csv = None, None
                if os.path.isdir(output_annual_dir):
                    for file in os.listdir(output_annual_dir):
                        if file.endswith('_channel_belt.csv'):
                            cb_csv = file
                        elif file.endswith('_mobility_metrics.csv'):
                            mobility_csv = file
                if cb_csv is not None and mobility_csv is not None:
                    cb_csv_path = os.path.join(output_annual_dir, cb_csv)
                    mobility_csv_path = os.path.join(output_annual_dir, mobility_csv)
                    channel_belt_df = pd.read_csv(cb_csv_path)
                    if not channel_belt_df.empty and 'cb_area_m2' in channel_belt_df.columns:
                        cb_value = channel_belt_df['cb_area_m2'].iloc[0]
                    else:
                        cb_value = np.nan
                    mobility_df = pd.read_csv(mobility_csv_path)
                    mobility_row = mobility_df[mobility_df['Quantile'] == 50]
                    if not mobility_row.empty and 'Aw' in mobility_row.columns:
                        aw_value = mobility_row['Aw'].iloc[0]
                    else:
                        aw_value = np.nan
                    if pd.notna(cb_value) and pd.notna(aw_value) and aw_value != 0:
                        cb_aw = cb_value / aw_value
                    else:
                        cb_aw = np.nan
                else:
                    cb_aw = np.nan
            common_data['CB/Aw'] = cb_aw

            # Retrieve T_R value: prioritize full_data, then fallback to mobility metrics file
            t_r_value = np.nan
            t_r_full_data = full_data[full_data['River'] == river_folder]['TR'].values
            if len(t_r_full_data) > 0:
                t_r_value = t_r_full_data[0]
            else:
                river_folder_path = os.path.join(root_dir, river_folder, 'output_annual', river_folder)
                mobility_metrics_csv = f"{river_folder}_mobility_metrics.csv"
                mobility_metrics_path = os.path.join(river_folder_path, mobility_metrics_csv)
                if os.path.exists(mobility_metrics_path):
                    mobility_df = pd.read_csv(mobility_metrics_path)
                    quantile_50_row = mobility_df[mobility_df['Quantile'] == 50]
                    if not quantile_50_row.empty:
                        t_r_value = quantile_50_row['T_R'].values[0]
            common_data['T_R'] = t_r_value

            # Discharge Calculations (annual statistics)
            average_discharge_annual = np.nan
            median_discharge_annual = np.nan
            cov_discharge_site = np.nan    # overall variability using all Q values (site)
            cov_discharge_temporal = np.nan  # variability from annual means (temporal)

            if pd.notna(galeazzi_row['ID_discharge']):
                discharge_file = f"{galeazzi_row['ID_discharge']}.csv"
                discharge_path = os.path.join(discharge_dir, discharge_file)
                if os.path.exists(discharge_path):
                    discharge_df = pd.read_csv(discharge_path)
                    discharge_df['date'] = pd.to_datetime(discharge_df['date'], format='%m/%d/%Y')
                    discharge_df['Year'] = discharge_df['date'].dt.year
                    annual_avg_discharge = discharge_df.groupby('Year')['Q'].mean()
                    average_discharge_annual = annual_avg_discharge.mean()
                    median_discharge_annual = discharge_df['Q'].median()
                    if average_discharge_annual != 0:
                        cov_discharge_temporal = annual_avg_discharge.std() / average_discharge_annual
                    else:
                        cov_discharge_temporal = np.nan
                    overall_mean_Q = discharge_df['Q'].mean()
                    if overall_mean_Q != 0:
                        cov_discharge_site = discharge_df['Q'].std() / overall_mean_Q
                    else:
                        cov_discharge_site = np.nan
            common_data.update({
                'average_discharge_annual': average_discharge_annual,
                'median_discharge_annual': median_discharge_annual,
                'cov_discharge_site': cov_discharge_site,
                'cov_discharge_temporal': cov_discharge_temporal
            })

            # Combine subannual, annual, and common data for the river
            combined_data = {**common_data, **subannual_data, **annual_data}
            combined_data.update(annual_data)
            combined_statistics_dfs.append(pd.DataFrame([combined_data]))

# Concatenate and save all DataFrames
combined_statistics_df = pd.concat(combined_statistics_dfs, ignore_index=True)

# Merge McLeod data into the combined statistics DataFrame based on 'River'
combined_statistics_df = pd.merge(
    combined_statistics_df,
    mcleod_df[['River', 'Qbf point']],
    on='River',
    how='left'
)

# Calculate Iw as Qm divided by Qbf point (avoid division by zero)
combined_statistics_df['Iw'] = combined_statistics_df.apply(
    lambda row: row['Qm'] / row['Qbf point'] if pd.notna(row['Qm']) and pd.notna(row['Qbf point']) and row['Qbf point'] != 0 else np.nan,
    axis=1
)

g   = 9.81       # [m/s²]
WDR = 20         # width‐to‐depth ratio (user‐set)
Cf  = 0.01       # calibration factor

# First, make sure all the needed columns are present in combined_statistics_df:
#   ['Qm', 'Width(m)', 'mean_bi_site', 'Slope (cm/km) ']

# Convert slope to dimensionless
combined_statistics_df['slope_dimless'] = combined_statistics_df['Slope (cm/km) '] * 1e-5

# Vectorized compute of dim_Q
combined_statistics_df['dim_Q'] = (
    combined_statistics_df['Qm'] * WDR**1.5
    / (
        np.sqrt(g)
        * (combined_statistics_df['Width(m)'] 
           * combined_statistics_df['mean_bi_site']**-1)**2.5
        * np.sqrt(combined_statistics_df['slope_dimless'] / Cf)
      )
)

# ---- New Section: Merge PIV migration data ----

# Load merged PIV file for migration rates and average wetted width
merged_piv_df = pd.read_csv(merged_piv_file)

# Remove any rows with non-positive migration rate (i.e. less than or equal to 0)
merged_piv_df = merged_piv_df[merged_piv_df['Mean migration rate [m/yr]'] > 0]

# Calculate normalized migration rate and error
merged_piv_df['norm_migration_rate'] = merged_piv_df['Mean migration rate [m/yr]'] / merged_piv_df['Average wetted width [m]']
merged_piv_df['norm_error'] = merged_piv_df['std. migration'] / merged_piv_df['Average wetted width [m]']

# Merge the PIV migration data into the combined statistics DataFrame based on River name
combined_statistics_df = pd.merge(
    combined_statistics_df,
    merged_piv_df[['River_Station', 'Mean migration rate [m/yr]', 'std. migration', 'norm_migration_rate', 'norm_error']],
    left_on='River',
    right_on='River_Station',
    how='left'
)

# Rename columns for clarity
combined_statistics_df.rename(columns={
    'Mean migration rate [m/yr]': 'mean_migration_rate',
    'std. migration': 'std_migration'
}, inplace=True)

# Optionally drop the duplicate River_Station column
combined_statistics_df.drop(columns=['River_Station'], inplace=True)

# Save the updated combined statistics DataFrame with the new statistics
output_filepath = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_combined_statistics.csv"
combined_statistics_df.to_csv(output_filepath, index=False)

print(f"Statistics saved to {output_filepath}.")
