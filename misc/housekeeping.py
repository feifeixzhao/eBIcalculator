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


# make sure all folders have the correct files: output subannual, output annual, prepared imagery subannual, prepared imagery annual
