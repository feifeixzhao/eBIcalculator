import os
import pandas as pd
import numpy as np

def compute_stats(arr):
    """Compute mean, median, std, 5th, and 95th percentiles for an array."""
    return {
        "mean": np.nanmean(arr),
        "median": np.nanmedian(arr),
        "std": np.nanstd(arr),
        "5th percentile": np.nanpercentile(arr, 5),
        "95th percentile": np.nanpercentile(arr, 95)
    }

##############################################
# PART A: Gather eBI and BI (and ratios) from all river folders
##############################################

# Define the root directory where each river folder is located
root_dir = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_results"

# Load combined statistics file to get classification mapping.
combined_statistics_path = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_combined_statistics.csv"
df_combined = pd.read_csv(combined_statistics_path, usecols=["River", "Classification", "CB/Aw", "T_R"])
# Create a mapping dictionary: River -> Classification
river2class = dict(zip(df_combined["River"], df_combined["Classification"]))

# We will accumulate values in a dictionary for each group and category.
# For each group ("Braided" and "Wandering"), we store lists for:
#  - Overall (site): eBI, BI, ratio
#  - Reach: yearly averages of eBI and BI, and their ratio
#  - Cross_section (xsection): cross-section averages (across years) of eBI and BI, and their ratio
groups = {"Braided": {"ebi": [], "bi": [], "ratio": [],
                      "ebi_reach": [], "bi_reach": [], "ratio_reach": [],
                      "ebi_xsection": [], "bi_xsection": [], "ratio_xsection": []},
          "Wandering": {"ebi": [], "bi": [], "ratio": [],
                        "ebi_reach": [], "bi_reach": [], "ratio_reach": [],
                        "ebi_xsection": [], "bi_xsection": [], "ratio_xsection": []}}

# Loop through each river folder
for river_folder in os.listdir(root_dir):
    river_path = os.path.join(root_dir, river_folder)
    if not os.path.isdir(river_path):
        continue
    # Get classification from mapping; skip if not present.
    classification = river2class.get(river_folder, None)
    if classification is None:
        continue
    if classification == "B":
        group = "Braided"
    elif classification in ["HSW", "LSW"]:
        group = "Wandering"
    else:
        continue

    # Look for annual CSV files in the "rivgraph" subfolder.
    rivgraph_path = os.path.join(river_path, "rivgraph")
    if not os.path.isdir(rivgraph_path):
        continue
    ebi_csv = os.path.join(rivgraph_path, "eBI_results_annual.csv")
    bi_csv = os.path.join(rivgraph_path, "BI_results_annual.csv")
    if not (os.path.exists(ebi_csv) and os.path.exists(bi_csv)):
        continue
    try:
        ebi_df = pd.read_csv(ebi_csv)
        bi_df = pd.read_csv(bi_csv)
    except Exception as e:
        print(f"Error reading files for {river_folder}: {e}")
        continue

    # Merge on Year and Cross_section.
    merged_df = pd.merge(ebi_df, bi_df, on=["Year", "Cross_section"], how="inner")
    if merged_df.empty:
        continue
    # Compute ratio for each observation (avoid division by zero)
    merged_df["ratio"] = merged_df["eBI"] / merged_df["BI"].replace(0, np.nan)

    # Overall (site) values: all observations
    groups[group]["ebi"].extend(merged_df["eBI"].dropna().tolist())
    groups[group]["bi"].extend(merged_df["BI"].dropna().tolist())
    groups[group]["ratio"].extend(merged_df["ratio"].dropna().tolist())

    # Reach: Group by Year, compute the mean per year, then add these values.
    reach_ebi = merged_df.groupby("Year")["eBI"].mean()
    reach_bi = merged_df.groupby("Year")["BI"].mean()
    reach_ratio = reach_ebi / reach_bi.replace(0, np.nan)
    groups[group]["ebi_reach"].extend(reach_ebi.dropna().tolist())
    groups[group]["bi_reach"].extend(reach_bi.dropna().tolist())
    groups[group]["ratio_reach"].extend(reach_ratio.dropna().tolist())

    # Cross_section: Group by Cross_section, compute the mean per cross_section, then add these.
    xsec_ebi = merged_df.groupby("Cross_section")["eBI"].mean()
    xsec_bi = merged_df.groupby("Cross_section")["BI"].mean()
    xsec_ratio = xsec_ebi / xsec_bi.replace(0, np.nan)
    groups[group]["ebi_xsection"].extend(xsec_ebi.dropna().tolist())
    groups[group]["bi_xsection"].extend(xsec_bi.dropna().tolist())
    groups[group]["ratio_xsection"].extend(xsec_ratio.dropna().tolist())

# Compute bulk statistics for each group and category for eBI, BI, ratio.
results_partA = []
for group in groups:
    for key, label in [("ebi", "Overall eBI"), ("bi", "Overall BI"), ("ratio", "Overall eBI/BI"),
                       ("ebi_reach", "Reach eBI"), ("bi_reach", "Reach BI"), ("ratio_reach", "Reach eBI/BI"),
                       ("ebi_xsection", "Xsection eBI"), ("bi_xsection", "Xsection BI"), ("ratio_xsection", "Xsection eBI/BI")]:
        arr = np.array(groups[group].get(key, []))
        if arr.size == 0:
            stats = {"mean": np.nan, "median": np.nan, "std": np.nan,
                     "5th percentile": np.nan, "95th percentile": np.nan}
        else:
            stats = compute_stats(arr)
        row = {"Group": group, "Category": label}
        row.update(stats)
        results_partA.append(row)
results_df_A = pd.DataFrame(results_partA)

##############################################
# PART B: Bulk stats for CB/Aw and T_R from combined stats file
##############################################
df_braided = df_combined[df_combined["Classification"] == "B"]
df_wandering = df_combined[df_combined["Classification"].isin(["HSW", "LSW"])]

stats_CB_Aw_braided = compute_stats(df_braided["CB/Aw"].dropna())
stats_T_R_braided = compute_stats(df_braided["T_R"].dropna())
stats_CB_Aw_wandering = compute_stats(df_wandering["CB/Aw"].dropna())
stats_T_R_wandering = compute_stats(df_wandering["T_R"].dropna())

results_partB = []
results_partB.append({
    "Group": "Braided", "Category": "CB/Aw",
    **stats_CB_Aw_braided
})
results_partB.append({
    "Group": "Braided", "Category": "T_R",
    **stats_T_R_braided
})
results_partB.append({
    "Group": "Wandering", "Category": "CB/Aw",
    **stats_CB_Aw_wandering
})
results_partB.append({
    "Group": "Wandering", "Category": "T_R",
    **stats_T_R_wandering
})
results_df_B = pd.DataFrame(results_partB)

##############################################
# PART C: Bulk stats for migration rates from migration file
##############################################
migration_file = r"C:\Users\Feifei\Box\BR_remote_sensing\merged_PIV_eBI_TR.csv"
df_migration = pd.read_csv(migration_file)
# Filter out negative migration rates
df_migration = df_migration[df_migration["Mean migration rate [m/yr]"] >= 0]

# Split based on the migration file's Classification column.
df_mig_braided = df_migration[df_migration["Classification"] == "B"]
df_mig_wandering = df_migration[df_migration["Classification"].isin(["HSW", "LSW"])]

stats_mig_braided = compute_stats(df_mig_braided["Mean migration rate [m/yr]"].dropna())
stats_mig_wandering = compute_stats(df_mig_wandering["Mean migration rate [m/yr]"].dropna())

# Compute normalized migration rate = Mean migration rate [m/yr] / Average wetted width [m]
df_migration["Normalized migration rate"] = df_migration["Mean migration rate [m/yr]"] / df_migration["Average wetted width [m]"]

df_norm_braided = df_migration[df_migration["Classification"] == "B"]
df_norm_wandering = df_migration[df_migration["Classification"].isin(["HSW", "LSW"])]

stats_norm_braided = compute_stats(df_norm_braided["Normalized migration rate"].dropna())
stats_norm_wandering = compute_stats(df_norm_wandering["Normalized migration rate"].dropna())

results_partC = []
results_partC.append({
    "Group": "Braided", "Category": "Mean migration rate [m/yr]",
    **stats_mig_braided
})
results_partC.append({
    "Group": "Wandering", "Category": "Mean migration rate [m/yr]",
    **stats_mig_wandering
})
results_partC.append({
    "Group": "Braided", "Category": "Normalized migration rate",
    **stats_norm_braided
})
results_partC.append({
    "Group": "Wandering", "Category": "Normalized migration rate",
    **stats_norm_wandering
})
results_df_C = pd.DataFrame(results_partC)

##############################################
# PART D: Combine all results and save to CSV
##############################################
final_df = pd.concat([results_df_A, results_df_B, results_df_C], ignore_index=True)

output_csv = r"C:\Users\Feifei\Box\BR_remote_sensing\bulk_stats_all_groups.csv"
final_df.to_csv(output_csv, index=False)

print("Bulk statistics for all variables have been computed and saved to:")
print(output_csv)
