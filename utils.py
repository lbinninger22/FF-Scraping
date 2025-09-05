import os
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import re
import requests
from cookieString import cookies

# NOTE: This method was removed as in very specific cases simply counting the number of teams
# and iterating from 1 to that number for the team IDs does not work.
# see: get_team_ids_for_season() below for more details
# NOTE: we can still get the number of owners by calling len(get_team_ids_for_season(...))
# #gets the total number of players in a given season
# def get_number_of_owners(leagueID, season) :
# 	owners_url = 'https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/owners'
# 	owners_page = requests.get(owners_url, cookies=cookies)
# 	owners_html = owners_page.text
# 	owners_soup = bs(owners_html, 'html.parser')
# 	number_of_owners = len(owners_soup.find_all('tr', class_ = re.compile('team-')))
# 	return number_of_owners

# get all team IDs for a given season
# in specific cases, a team may have an id > the number of teams
# e.g. a new team joins in 2019 to a league of 10 teams and gets id #9
# -> in 2020 the league gets reduced to 8 teams, but the team retains id #9
def get_team_ids_for_season(leagueID, season):
    owners_url = 'https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/owners'
    owners_page = requests.get(owners_url, cookies=cookies)
    owners_html = owners_page.text
    owners_soup = bs(owners_html, 'html.parser')
    team_ids = []
    # extract all the team IDs from the table rows
    for owner_row in owners_soup.find_all('tr', class_ = re.compile('team-')):
        # get class element where team ID is stored as a list
        # different classes in html are separated by spaces
        class_list = owner_row.get('class', [])

        # find the class with the team ID
        for cls in class_list:
            # match the regex pattern that starts iwth "team-" followed by digits
            match = re.match(r'team-(\d+)', cls)
            if match:
                # extract the team ID from the matched pattern
                # group(0) is the full match, group(1) is the first captured group (the digits)
                team_id = match.group(1)
                break
        
        # append the team ID to the list
        team_ids.append(int(team_id))
        
    return team_ids

def setup_output_folders(leagueID, season):
    path = "./output/"
    if not os.path.isdir(path):
        os.mkdir(path)

    games_path = path + leagueID + "-history-teamgamecenter/"
    if not os.path.isdir(games_path):
        os.mkdir(games_path)

    games_path += season + "/"
    if not os.path.isdir(games_path):
        os.mkdir(games_path)

    standings_path = "./output/" + leagueID + "-history-standings/"
    if not os.path.isdir(standings_path):
	    os.mkdir(standings_path)
