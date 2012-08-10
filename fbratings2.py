#!/usr/bin/python

import sys, string, re, math

# Create a list called schedule. This list will contain dictionaries of games.
schedule = []

# Create a list called teamlist.  This list will contain dictionaries of teams.
teamlist = []

def totalPtsGame (score1, score2):
	return score1 + score2

###############################################################################
# This returns the average points scored per game per team.                   #
###############################################################################	
def avgPtsGame (totalPts, totalGms):
	return float(totalPts)/totalGms/2

###############################################################################
# We adjust the score here to prevent a team from running up the score.  This #
# uses the law of diminishing returns. For instance, a score of 20 will have  #
# an adjusted score of 18.4 whereas a score of 50 will have an adjusted score #
# of 40.0.                                                                    #
###############################################################################
def adjustScore (score):
	adjScore = score - (score * score)/250.0
	return adjScore

###############################################################################
# The expectedGameResult is used to determine an expected outcome of a game.   #
# The expected outcome is determined by comparing the ratings of the two      #
# teams involved in the game.  An expected ratio of 1.0 would mean that one   #
# team has a 100% chance of winning.  An expected ratio of 0.5 would mean     #
# that each team has a 50% chance of winning.                                 #
###############################################################################
def expectedGameResult (rating1, rating2, x):
	expRatio = (1 / (1 + pow(10, (rating2 - rating1) / x)))
	return expRatio

###############################################################################
# The calcGameRatio is used to determine the actual outcome of the game in a  #
# format that is equivalent to the expectedGameResult.  We divide the adjusted #
# score for each team by six since that is the greatest number of points a    #
# team can score at one time (i.e. a touchdown).  We add 1.0 in the numerator #
# and 2.0 in the denominator to ensure that if the score is 0 to 0, the       #
# function will return 0.5 instead of a divide by zero error.  The winning    #
# team also gains an additional 1 point as a bonus whereas if the teams tie   #
# each team receives an additional 0.5 points.                                #
###############################################################################
def calcGameRatio (score1,score2):
	adjScore1 = pow((adjustScore(score1))/6.0,2)
	adjScore2 = pow((adjustScore(score2))/6.0,2)
	gameRatio = (adjScore1 + 1.0) / (adjScore1 + adjScore2 + 2.0)
	if score1 > score2:
		gameRatio = gameRatio + 1.0
	else:
		if score1 == score2:
			gameRatio = gameRatio + 0.5
	return gameRatio * 0.5

###############################################################################
# We call this function when we need to add a team to the teamlist.  We set   #
# all values to 0 except for the team's rating which is set to 50.0.          #
###############################################################################
def addTeam (name):
	team = {'name': name,
			'won': 0,
			'lost': 0,
			'tied': 0,
			'pf': 0,
			'pa': 0,
			'hwon': 0,
			'hlost': 0,
			'htied': 0,
			'hpf': 0,
			'hpa': 0,
			'vwon': 0,
			'vlost': 0,
			'vtied': 0,
			'vpf': 0,
			'vpa': 0,
			'grate': 0.0,
			'rating': 50.0,
			'sched': 0.0
			}
	teamlist.append(team)

###############################################################################
# This function is used to lookup a team in the teamlist.  If the team is not #
# located, then we call the addTeam function.                                 #
###############################################################################	
def lookupTeam (teamname):

	for row in teamlist:
		if teamname == row['name']:
			break
	else:
		addTeam (teamname)

		
###############################################################################
# This function updates the won-lost-tied record and points scored and points #
# allowed for each of the two teams involved in a game.                       #
###############################################################################
def updateTeamStats (team1, score1, team2, score2):
	lookupTeam (team1)
	lookupTeam (team2)
	for t in teamlist:
		if team1 == t['name']:
			t['pf']    = t['pf'] + score1
			t['pa']    = t['pa'] + score2
			if (score1 > score2):
				t['won'] = t['won'] + 1
			else:
				if (score1 < score2):
					t['lost'] = t['lost'] + 1
				else:
					t['tied'] = t['tied'] + 1
		else:
			if team2 == t['name']:
				t['pf']  = t['pf'] + score2
				t['pa']  = t['pa'] + score1
				if (score1 < score2):
					t['won'] = t['won'] + 1
				else:
					if (score1 > score2):
						t['lost'] = t['lost'] + 1
					else:
						t['tied'] = t['tied'] + 1

###############################################################################
# This function is used to lookup a team's grate.                             #
###############################################################################
def lookupTeamRate (team):
	for t in teamlist:
		if team == t['name']:
			return t['grate']

###############################################################################
# This function is used to update a team's grate.  The grate is the           #
# difference between the actual outcome and expected outcome.  The grate is   #
# an accumulated amount.  It gets reset to 0 each time score's are read.      #
# After all scores have been read, the accumulated grate is used for changing #
# a team's rating.                                                            #
###############################################################################			
def updateTeamRate (team, rate):
	for t in teamlist:
		if team == t['name']:
			t['grate'] = rate

###############################################################################
# This is used to lookup a team's rating.                                     #
###############################################################################
def lookupTeamRating (team):
	for t in teamlist:
		if team == t['name']:
			return t['rating']

###############################################################################
# This function is used to update a team's rating.  The teams rating is       #
# calculated by dividing the accumulated grate by the number of games played  #
# for the team and then multiplying the result with the kfactor.  The result  #
# from this is added to the existing rating to make a new team rating.        #
###############################################################################
def updateTeamRating (kfactor):
	for t in teamlist:
			t['rating'] = t['rating'] + (kfactor * (t['grate'] / (t['won'] + t['lost'] + t['tied'])))

def sortDictBy (list, key):
	nlist = map(lambda x, key=key: (x[key], x), list)
	nlist.sort()
	return map(lambda (key, x): x, nlist)

def sortDictByDesc (list, key):
	nlist = map(lambda x, key=key: (x[key], x), list)
	nlist.sort()
	nlist.reverse()
	return map(lambda (key, x): x, nlist)

def calcTeamRatings(totalgames):
	Kfactor = 10.0
	tolerance = 1e-9
	stdDevRatio = 1.0
	max_iterations = 25000
	stdDevRatioDiff = 100.0
	oldstdDevRatio = 1.0
	iterations = 0
	print "Calculating ratings..."
	while ((stdDevRatioDiff > tolerance) and (iterations < max_iterations)):
		oldstdDevRatio = stdDevRatio
		sum_grate = 0.0
		for t in teamlist:
			t['grate'] = 0.0
		for g in schedule:
			team1grate = lookupTeamRate(g['team1'])
			team1rating = lookupTeamRating(g['team1'])
			team2grate = lookupTeamRate(g['team2'])
			team2rating = lookupTeamRating(g['team2'])
			team1grate = team1grate + g['ratio'] - expectedGameResult(team1rating, team2rating, Kfactor)
			team2grate = team2grate + 1 - g['ratio'] - (1 - expectedGameResult(team1rating, team2rating, Kfactor))
			updateTeamRate (g['team1'], team1grate)
			updateTeamRate (g['team2'], team2grate)
			sum_grate = sum_grate + team1grate	
		# Calculate grate standard deviation
		stdDevRatio = math.sqrt(((sum_grate * sum_grate) / totalgames))
		stdDevRatioDiff = pow(oldstdDevRatio - stdDevRatio, 2)
		#if (not(iterations % 250)):
		#	print "Game ratio standard deviation:", stdDevRatio
		iterations = iterations + 1
		updateTeamRating(Kfactor)
	if (iterations > max_iterations):
		print "Fatal error: Game ratios aren't converging."
	else:
	#	print "Congratulations! Game Ratios have converged!"
		print "The program ran through the scores", iterations, "times!"

###############################################################################
# We call this function to print the standings.                               #
###############################################################################
def printStandings(teamlist):
	print ('%-28s %4s %5s %5s %5s %5s %8s %6s' % ('', 'Won', 'Lost', 'Tied', 'PF', 'PA', 'Rating', 'SOS'))
	teamlist = sortDictByDesc(teamlist, "rating")
	for team in teamlist:
		print ('%-28s %4s %5s %5s %5s %5s %8.3f %6s' % (team['name'], team['won'], team['lost'], team['tied'], team['pf'], team['pa'], team['rating'], team['sched']))

###############################################################################
# We use regular expressions to read the input file.  The format used is:     #
# date, team1, team1score, team2, team2score, location.  These fields may be  #
# separated by spaces or tabs which is why we need to use regular expressions.#
###############################################################################
#pattern = re.compile(r'^(.*\D\d+\D\d+)\D(.*)\D(.*\d+)\D(.*)\D(.*\d+)(.*)$')
#pattern = re.compile(r'^(.*\D\d+\D\d+)\D(.*)\D(.*\d+)\D(.*)\D(.*\d+)(.*\d)$')
pattern = re.compile(r'^(.*\D\d+\D\d+)\D(.*)\D(.*\d+)\D(.*)\D(.*\d+)$')
###############################################################################
# Open the input file which is obtained from the command line argument.       #
###############################################################################
filename = sys.argv[1]
file = open (filename, 'r')

###############################################################################
# We want to read in the game results and store each game as a dictionary in  #
# the game list we created.  Then we close the input file.                    #
###############################################################################
while True:
	line = file.readline ()
	if not line: break
	g = {}						# define dictionary
	g['date'], g['team1'], g['score1'], g['team2'], g['score2'] = pattern.search(line).groups()
	# strip trailing whitespace from team names
	g['team1'] = string.strip (g['team1'])
	g['team2'] = string.strip (g['team2'])
	g['score1'] = int(g['score1'])
	g['score2'] = int(g['score2'])
	schedule.append(g)
file.close()

###############################################################################
# Initialize totalpoints and totalgames to 0.  These variables will be used   #
# to calculate average points scored per game per team.                       #
###############################################################################	
totalpoints = 0
totalgames = 0

for g in schedule:
	# Get the total number of points scored for the game and add to totalpoints
	#totalpoints = totalpoints + totalPtsGame (g['score1'], g['score2'])
	totalpoints = totalpoints + g['score1'] + g['score2']
  
	# Add the field ratio to the game dictionary and call calcGameRatio to get
    # the result.
	g['ratio'] = calcGameRatio (g['score1'], g['score2'])

	# Update the won-lost-tied record and points scored and points allowed for
	# the two teams involved in the game.
	updateTeamStats (g['team1'], g['score1'], g['team2'], g['score2'])

	# Update the totalgames played
	totalgames = totalgames + 1

print ""
print totalgames, "games successfully read"
print "Average points per team per game:", avgPtsGame(totalpoints, totalgames)

calcTeamRatings(totalgames)

printStandings(teamlist)
