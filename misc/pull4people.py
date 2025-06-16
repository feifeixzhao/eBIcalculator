import pandas as pd

# File paths for the CSV files
galeazzi_file_path = r"C:\Users\Feifei\Box\BR_remote_sensing\Galeazzi_eBI.csv"
combined_stats_file_path = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_results\ebi_combined_statistics.csv"

# Load the Galeazzi CSV file
galeazzi_df = pd.read_csv(galeazzi_file_path)

# Filter rows where both 'PIV? ' and 'eBI (N=no, P=potential, Y=yes)?' are 'Y'
filtered_df = galeazzi_df[(galeazzi_df['PIV?'] == 'Y') & 
                          (galeazzi_df['eBI (N=no, P=potential, Y=yes)?'] == 'Y')][['River_Station', 'Classification']]

# Load the combined statistics CSV file
combined_stats_df = pd.read_csv(combined_stats_file_path)

# Merge the filtered dataframe with the combined statistics dataframe on river names
merged_df = pd.merge(filtered_df, 
                     combined_stats_df[['River', 'T_R', 'Mean_eBI_annual', 'dim_Q']], 
                     left_on='River_Station', 
                     right_on='River', 
                     how='left')

# Keep only relevant columns in the final output
final_df = merged_df[['River_Station', 'Classification', 'dim_Q', 'T_R', 'Mean_eBI_annual']]

# File path for the new CSV file
output_file_path = r"C:\Users\Feifei\Box\BR_remote_sensing\merged.csv"

# Save the final dataframe to a new CSV file
final_df.to_csv(output_file_path, index=False)

print(f"Final merged CSV saved at: {output_file_path}")
