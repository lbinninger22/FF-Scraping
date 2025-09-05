import os
import csv

from utils import get_team_ids_for_season
from constants import gamecenter_directory, leagueID

# Script which iterates over all games, and finds the biggest blowouts, and narrowest victories.
largest_margin = 0
narrowest_margin = 1000

# Iterate through each year
for year in os.listdir(gamecenter_directory):
    print(year)
    path = gamecenter_directory + year + '/'
    # num_owners = len(get_team_ids_for_season(leagueID, path))
    
    # Iterate through each week
    for filename in os.listdir(path):
        if filename.endswith(".csv"):
            filepath = os.path.join(path, filename)
            with open(filepath, 'r', newline='') as file:
                reader = csv.DictReader(file)
                
                # Iterate through each team in the week
                for row in reader:
                    # Skip weeks where the team had a bye
                    if row['Total'] == "-" or row['Opponent Total'] == "-":
                        continue
                    # Calculate the margin of victory
                    margin = float(row['Total']) - float(row['Opponent Total'])
                    if margin > largest_margin:
                        largest_margin = margin
                    if margin > 0 and margin < narrowest_margin:
                        narrowest_margin = margin


