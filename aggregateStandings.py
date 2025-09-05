import csv
import os

from utils import get_team_ids_for_season
from constants import leagueID, standings_directory

# Aggregates scraped standings data into a single CSV file
# Assumptions:
# Top half of the league makes the playoffs

# Initialize a dictionary to store aggregated data
aggregated_data = {}

# Iterate through each file in the directory
for filename in os.listdir(standings_directory):
    if filename.endswith(".csv"):
        filepath = os.path.join(standings_directory, filename)
        with open(filepath, 'r', newline='') as file:
            reader = csv.DictReader(file)
            num_owners = len(get_team_ids_for_season(leagueID, filename[:-4]))
            # Iterate through each row in the CSV file
            for row in reader:
                manager_name = row["ManagerName"]

                # Initialize the manager's data if it doesn't exist
                if manager_name not in aggregated_data:
                    cols = ["PointsFor","PointsAgainst","Moves","Trades","Wins","Losses","Ties","Championships","Finals","Playoffs","Sackos","DraftPosition"]
                    aggregated_data[manager_name] = {col: 0 for col in cols}
                    aggregated_data[manager_name]["Seasons"] = 1
                else:
                    aggregated_data[manager_name]["Seasons"] += 1
                # Sum the values for each column except "ManagerName"
                for key, value in row.items():
                    if key in ["PointsFor", "PointsAgainst", "Moves", "Trades", "DraftPosition"]:
                        aggregated_data[manager_name][key] += float(value.replace(",", ""))
                    elif key == "Record":
                        wins, losses, ties = map(int, value.split("-"))
                        aggregated_data[manager_name]["Wins"] += wins
                        aggregated_data[manager_name]["Losses"] += losses
                        aggregated_data[manager_name]["Ties"] += ties
                    elif key == "PlayoffRank":
                        if int(value) == 1:
                            aggregated_data[manager_name]["Playoffs"] += 1
                            aggregated_data[manager_name]["Championships"] += 1
                            aggregated_data[manager_name]["Finals"] += 1
                        elif int(value) == 2:
                            aggregated_data[manager_name]["Playoffs"] += 1
                            aggregated_data[manager_name]["Finals"] += 1
                        elif int(value) == num_owners:
                            aggregated_data[manager_name]["Sackos"] += 1
                        # TODO: not every league has the top half in playoffs, e.g. some have 6/8 teams
                        elif int(value) <= int(num_owners/2):
                            aggregated_data[manager_name]["Playoffs"] += 1

# After looping through all files, the number of seasons is final
# Average DraftPosition over the number of seasons
for manager_name in aggregated_data:
    aggregated_data[manager_name]["DraftPosition"] = round(aggregated_data[manager_name]["DraftPosition"] / aggregated_data[manager_name]["Seasons"], 1)
    # also round PointsFor and PointsAgainst to 2 decimal places
    aggregated_data[manager_name]["PointsFor"] = round(aggregated_data[manager_name]["PointsFor"], 2)
    aggregated_data[manager_name]["PointsAgainst"] = round(aggregated_data[manager_name]["PointsAgainst"], 2)

# Convert dict_keys to a list
column_names = list(aggregated_data.values())[0].keys()

# Write the aggregated data to a new CSV file
output_filepath = './output/aggregated_standings_data.csv'
with open(output_filepath, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["ManagerName"] + list(column_names))
    # Write the aggregated data to the CSV file
    writer.writeheader()
    for manager_name, data in aggregated_data.items():
        data["ManagerName"] = manager_name
        writer.writerow(data)

print(f"Aggregated data written to {output_filepath}")