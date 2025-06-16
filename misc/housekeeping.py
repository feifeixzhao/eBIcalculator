# misc code to prep eBI folders for use with RivGraph

# make sure spreadsheet rivers have folders, delete the ones that don't 
import os
import pandas as pd
import shutil

csv_path = r"C:\Users\Feifei\Box\BR_remote_sensing\Galeazzi_eBI.csv"
directory_path = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_results"

# df = pd.read_csv(csv_path)
# valid_stations = df[df["eBI (N=no, P=potential, Y=yes)?"] == "Y"]["River_Station"].tolist()

# all_folders = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

# for folder in all_folders:
#     if folder not in valid_stations:
#         folder_path = os.path.join(directory_path, folder)
#         shutil.rmtree(folder_path)
#         print(f"Deleted folder: {folder}")

# remaining_folders = len([folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))])
# print(f"Remaining folders in the directory: {remaining_folders}")


# make sure ouputs dswe folder is labeled with subannual or annual 

for river_folder in os.listdir(directory_path):
    river_folder_path = os.path.join(directory_path, river_folder)
    if os.path.isdir(river_folder_path):
        prepared_imagery_path = os.path.join(river_folder_path, "PreparedImagery")
        output_path = os.path.join(river_folder_path, "output")

        # Rename "PreparedImagery" to "PreparedImagery_subannual"
        if os.path.exists(prepared_imagery_path):
            new_prepared_imagery_path = os.path.join(river_folder_path, "PreparedImagery_subannual")
            os.rename(prepared_imagery_path, new_prepared_imagery_path)

        # Rename "output" to "output_subannual"
        if os.path.exists(output_path):
            new_output_path = os.path.join(river_folder_path, "output_subannual")
            os.rename(output_path, new_output_path)

print("Renaming completed.")


# make sure all csv files end with _annual or _subannual


# Loop through each river folder in the specified directory
for river_folder in os.listdir(directory_path):
    river_folder_path = os.path.join(directory_path, river_folder)
    
    if os.path.isdir(river_folder_path):
        # Path for rivgraph folder
        rivgraph_path = os.path.join(river_folder_path, "rivgraph")
        
        # Check if rivgraph folder exists
        if os.path.exists(rivgraph_path) and os.path.isdir(rivgraph_path):
            # Iterate through CSV files in rivgraph folder
            for file_name in os.listdir(rivgraph_path):
                file_path = os.path.join(rivgraph_path, file_name)
                
                # Check if it’s a CSV file and does not end with "_annual" or "_subannual"
                if file_name.endswith(".csv") and not (file_name.endswith("_annual.csv") or file_name.endswith("_subannual.csv")):
                    new_file_name = file_name.replace(".csv", "_subannual.csv")
                    new_file_path = os.path.join(rivgraph_path, new_file_name)
                    os.rename(file_path, new_file_path)

print("Renaming completed.")

import pandas as pd

# Read the CSV files
df_stats = pd.read_csv(r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_combined_statistics.csv")
df_zhao = pd.read_csv(r"C:\Users\Feifei\Box\BR_remote_sensing\eBI_Zhao.csv")

# Optional: Remove any extra whitespace from the column headers
df_stats.columns = df_stats.columns.str.strip()
df_zhao.columns = df_zhao.columns.str.strip()

# Merge the DataFrames using custom suffixes to differentiate overlapping column names
merged_df = pd.merge(
    df_stats, 
    df_zhao, 
    left_on="River", 
    right_on="River_Station", 
    how="inner", 
    suffixes=('_stats', '_zhao')
)

# Select the desired columns:
# - 'River' from df_stats,
# - 'mean_ebi_site' from df_stats,
# - 'Classification_zhao' from df_zhao (which we rename to 'Classification'),
# - 'Latitude (deg)' and 'Longitude (deg)' from df_zhao.
final_df = merged_df[['River', 'mean_ebi_site', 'Classification_zhao', 'Latitude (deg)', 'Longitude (deg)']]

# Rename 'Classification_zhao' to 'Classification'
final_df.rename(columns={'Classification_zhao': 'Classification'}, inplace=True)

# Save the final DataFrame to a new CSV file
final_df.to_csv(r"C:\Users\Feifei\Box\BR_remote_sensing\world_map.csv", index=False)

# Print the first few rows to verify
print(final_df.head())

## separate wandering and braided
import pandas as pd

# Path to the combined statistics file
input_path = r"C:\Users\Feifei\Box\BR_remote_sensing\combined_ebi_wbm.csv"

# Load the DataFrame
df = pd.read_csv(input_path)

# Filter for wandering rivers (Classification "HSW" or "LSW")
df_wandering = df[df['Classification'].isin(['HSW', 'LSW'])]

# Filter for braided rivers (Classification "B")
df_braided = df[df['Classification'] == 'B']

# Save the filtered DataFrames to CSV files
df_wandering.to_csv(r"C:\Users\Feifei\Box\BR_remote_sensing\df_wandering.csv", index=False)
df_braided.to_csv(r"C:\Users\Feifei\Box\BR_remote_sensing\df_braided.csv", index=False)

print("Data saved as df_wandering.csv and df_braided.csv")
