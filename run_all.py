import csv
import subprocess

# Define the path to your CSV file
csv_file_path = r'C:\Users\Feifei\Box\BR_remote_sensing\Galeazzi_eBI.csv'

# Define the path to your rivgraph script
rivgraph_script_path = r'C:\Users\Feifei\PHD\eBIcalculator\rivgraph_eBI.py'

# Read the CSV file and execute the command for each relevant river
with open(csv_file_path, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        if row['eBI (N=no, P=potential, Y=yes)?'] == 'Y':
            river_name = row['River_Station']
            exit_sides = row['polygon ']
            command = f"python {rivgraph_script_path} --river_name {river_name} --exit_sides {exit_sides}"
            print(f"Executing command: {command}")
            subprocess.run(command, shell=True)

print("All rivers processed.")
