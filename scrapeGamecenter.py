  
import csv
import os
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import re
import requests
from cookieString import cookies
from utils import get_number_of_owners, setup_output_folders
from constants import leagueID, leagueStartYear, leagueEndYear, gamecenter_directory

#teams that don't fill all their starting roster spots for a week will have a longer bench
#the more roster spots left unfilled, the more bench players that team will have
#this method gets the teamid of the team with the longest bench for the week as well as the length of their bench
def get_longest_bench(week) :
	longest_bench_data = [0, 0]
	for i in range (1, number_of_owners + 1) :
		page = requests.get('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=' + str(i) + '&week=' + str(week), cookies=cookies)
		soup = bs(page.text, 'html.parser')
		print(i)
		#page.close()

		bench_div = soup.find('div', id='tableWrapBN-1')
		# in the edge case that a team has no bench players, this div might not exist, so we just set an empty list
		if bench_div:
			bench = bench_div.find_all('td', class_='playerNameAndInfo')
		else:
			bench = []

		# determine whether the current team has the longest bench
		if(len(bench) > longest_bench_data[0]) :
			longest_bench_data = [len(bench), i]

	return longest_bench_data

#generates the header for the csv file for the week
#different weeks can have different headers if players do not fill all their starting roster spots
def get_header(week, longest_bench_teamID) :
	url = "https://fantasy.nfl.com/league/" + leagueID + "/history/" + season + "/teamgamecenter?teamId=" +str(longest_bench_teamID) + "&week=" + str(week)
	page = requests.get(url, cookies=cookies)
	html = page.text
	page.close()
	soup = bs(html, 'html.parser') #uses the page of the teamID with the longest bench to generate the header

	position_tags = [tag.find('span').text for tag in soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('tr', class_ = re.compile('player-'))]
	#position tags are the label for each starting roster spot. different leagues can have different configurations for their starting rosters

	header = [] #csv file header

	#adds the position tags to the header. each tag is followed by a column to record the player's points for the week
	for i in range(len(position_tags)) :
		header.append(position_tags[i])
		header.append('Points')

	header = ['Owner',  'Rank'] + header + ['Total', 'Opponent', 'Opponent Total']

	return header

#gets one row of the csv file
#each row is the weekly data for one team in the league
def getrow(teamId, week, longest_bench) : 

	#loads gamecenter page as soup
	page = requests.get('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=' + teamId + '&week=' + week, cookies=cookies)
	soup = bs(page.text, 'html.parser')
	page.close()

	owner = soup.find('span', class_ = re.compile('userName userId')).text #username of the team owner

	starters = soup.find('div', id = 'tableWrap-1').find_all('td', class_ = 'playerNameAndInfo')
	starters = [starter.text for starter in starters]

	bench_div = soup.find('div', id='tableWrapBN-1')
	# in the edge case that a team has no bench players, this div might not exist, so we just set an empty list
	if bench_div:
		bench = bench_div.find_all('td', class_='playerNameAndInfo')
		bench = [benchplayer.text for benchplayer in bench]
	else:
		bench = []
	
	# in order to keep the row properly aligned, bench spots that are filled by another team
	# but not by this team are filled with a -
	while len(bench) < longest_bench: 
		bench.append('-')

	roster = starters + bench #every player on the team roster, in the order they are listed in game center, for the given week

	player_totals = soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('td', class_ = re.compile("statTotal"))
	player_totals = [player.text for player in player_totals] #point totals for each player with indecies which correspond to that player's index in roster

	teamtotals = soup.find_all('div', class_ = re.compile('teamTotal teamId-')) #the team's total points for the week
	ranktext = soup.find('span', class_ = re.compile('teamRank teamId-')).text
	rank = ranktext[ranktext.index('(') + 1: ranktext.index(')')] #the team's rank in the standings
	rosterandtotals = [] #alternating player names and their corresponding weekly point totals
	for i in range(len(roster)) :
		rosterandtotals.append(roster[i])

		#checks if there is a point total corresponding to the player, if not that spot is filled with a -
		try:
			rosterandtotals.append(player_totals[i])
		except:
			rosterandtotals.append('-')

	#try except statement is for the situation where the league member would not have an opponent for the week
	#in this case the Opponent and Opponent Total columns are filled with -
	try:
		completed_row = [owner, rank] + rosterandtotals + [teamtotals[0].text, soup.find('div', class_ = 'teamWrap teamWrap-2').find('span', re.compile('userName userId')).text, teamtotals[1].text]
	except:
		completed_row = [owner, rank] + rosterandtotals + [teamtotals[0].text, '-', '-']

	return completed_row


# Iterate through each season
# Iterate through each week
# Iterate through each team
# Write team's gamecenter data to a csv file
for s in range(leagueStartYear, leagueEndYear):
	season = str(s)
	# setup
	setup_output_folders(leagueID, season)

	page = requests.get('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=1&week=1', cookies=cookies)
	soup = bs(page.text, 'html.parser')
	season_length = len(soup.find_all('li', class_ = re.compile('ww ww-'))) #determines how may unique csv files are created, total number of weeks in the season 
	number_of_owners = get_number_of_owners(leagueID, season)

	print("Number of Owners: " + str(number_of_owners))
	print("Season Length: " + str(season_length))

	#Iterate through each week of the season, creating a new csv file every loop
	for i in range(1, season_length + 1): 
		longest_bench = get_longest_bench(i) #a list containing the length of the longest bench followed by the ID of the team with the longest bench
		header = get_header(i, longest_bench[1]) #header for the csv
		with open(gamecenter_directory + season + '/' + str(i) + '.csv', 'w', newline='') as f :
			writer = csv.writer(f)
			writer.writerow(header) #writes header as the first line in the new csv file
			for j in range(1, number_of_owners + 1) : #iterates through every team owner
				writer.writerow(getrow(str(j), str(i), longest_bench[0])) #writes a row for each owner in the csv
		print("Week " + str(i) + " Complete")
	print("Done")