import sys
import string
import math
import csv
from operator import itemgetter


def adjustScore(score,sport):
    '''We adjust the score here to prevent a team from running up the
    score.
    '''
    if sport == 'football':
        score_factor = 250.0
    elif sport == 'basketball':
        score_factor = 750.0
    else:
        score_factor = 100.0
    adjScore = score - (score * score)/score_factor
    return adjScore

def expectedGameResult (rating1, rating2, x):
    '''The expectedGameResult method is used to determine an expected
    outcome of a game. The expected outcome is determined by comparing
    the ratings of the two teams involved in the game. An expected ratio
    of 1.0 would mean that one team has a 100% chance of winning. An
    expected ratio of 0.5 would mean that each team has a 50% chance of
    winning.

    '''
    expRatio = (1 / (1 + pow(10, (rating2 - rating1) / x)))
    return expRatio

def calcGameRatio (score1,score2,sport):
    '''The calcGameRatio method is used to determine the actual outcome
    of the game in a format that is equivalent to the expectedGameResult.
    We divide the adjusted score for each team by the greatest number of
    points a team can score at one time (i.e. 6 in football,
    3 in basketball, 1 in baseball and hockey). We add 1.0 in the
    numerator and 2.0 in the denominator to ensure that if the score is
    0 to 0, the function will return 0.5 instead of a divide by zero
    error.  The winning team also gains an additional 1 point as a bonus
    whereas if the teams tie each team receives an additional 0.5 points.

    '''
    if sport == 'football':
        max_score = 6.0
    elif sport == 'basketball':
        max_score = 3.0
    else:
        max_score = 1.0

    adjScore1 = pow((adjustScore(score1,sport))/max_score,2)
    adjScore2 = pow((adjustScore(score2,sport))/max_score,2)
    gameRatio = (adjScore1 + 1.0) / (adjScore1 + adjScore2 + 2.0)
    if score1 > score2:
        gameRatio = gameRatio + 1.0
    else:
        if score1 == score2:
            gameRatio = gameRatio + 0.5
    return gameRatio * 0.5

def initTeam (teamlist, name):
    '''The initTeam function is used to add a team to the teamlist.  All
    values are set to 0 except for the rating which is set to 50.0.

    '''
    teaminfo = {'name': name,
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
            'game_rate_accum': 0.0,
            'power': 50.0,
            'sched_strength': 0.0,

            }
    teamlist.append(teaminfo)

def lookupTeam (teamlist, teamname):
    '''The lookupTeam function is used to look up a team in the teamlist.
    If the team is not located, then we call the addTeam function.

    '''
    for team in teamlist:
        if teamname == team['name']:
            return team
    else:
        initTeam(teamlist, teamname)
        for team in teamlist:
            if teamname == team['name']:
                return team

def updateTeamStats (teamlist, team1, score1, team2, score2):
    '''The updateTeamStats function updates the won-lost-tied record and pts
    scored and pts allowed for each of the two teams involved in a game.

    '''
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

def lookupTeamRate(teamlist, team):
    for t in teamlist:
        if team == t['name']:
            return t['game_rate_accum']

def updateTeamRate(teamlist, team, rate):
    for t in teamlist:
        if team == t['name']:
            t['game_rate_accum'] = rate

def lookupTeamRating(teamlist, team):
    for t in teamlist:
        if team == t['name']:
            return t['power']

def updateTeamRating(teamlist, kfactor):
    for t in teamlist:
        t['power'] = t['power'] + (kfactor * (t['game_rate_accum'] / (t['won'] + t['lost'] + t['tied'])))

def printSummary(total_games, total_points):
    avg_pts_game = float(total_points / total_games / 2)
    print("The total number of games played is", total_games)
    print("The total number of points scored is", total_points)
    print("The average number of points scored per team per game is %0.3f" \
                                                    % avg_pts_game)

def calcTeamRatings(teamlist, totalgames, schedule):
    '''The calcTeamRatings method calculates each teams' power ratings.'''
    kfactor = 10.0
    tolerance = 1e-9
    stdDevRatio = 1.0
    max_iterations = 25000
    stdDevRatioDiff = 100.0
    oldStdDevRatio = 1.0
    iterations = 0
    print("Calculating Power Ratings...")
    while ((stdDevRatioDiff > tolerance) and (iterations < max_iterations)):
        oldStdDevRatio = stdDevRatio
        total_game_rate_accum = 0.0
        for t in teamlist:
            t['game_rate_accum'] = 0.0
        for g in schedule:
            team1grate = lookupTeamRate(teamlist, g['team1'])
            team1rating = lookupTeamRating(teamlist, g['team1'])
            team2grate = lookupTeamRate(teamlist, g['team2'])
            team2rating = lookupTeamRating(teamlist, g['team2'])
            team1grate = team1grate + g['game_ratio'] - expectedGameResult(team1rating, team2rating, kfactor)
            team2grate = team2grate + 1 - g['game_ratio'] - (1 - expectedGameResult(team1rating, team2rating, kfactor))
            updateTeamRate(teamlist, g['team1'], team1grate)
            updateTeamRate(teamlist, g['team2'], team2grate)
            total_game_rate_accum = total_game_rate_accum + team1grate
        # Calculate grate standard deviation
        stdDevRatio = math.sqrt(((total_game_rate_accum * total_game_rate_accum) / totalgames))
        stdDevRatioDiff = pow(oldStdDevRatio - stdDevRatio, 2)
        iterations = iterations + 1
        updateTeamRating(teamlist, kfactor)
    if (iterations > max_iterations):
        print("Fatal error: Game ratios aren't converging")
    else:
        print("The scores were examined", iterations, "times.")

def sortDictByDesc(list, key):
    sortedlist = sorted(list, key=itemgetter('power'))
    sortedlist.reverse()
    return sortedlist

def printRankings(teamlist):
    '''The printRankings method returns the calculated rankings

    '''
    print ('%-28s %4s %5s %5s %5s %5s %8s %6s' % ('', 'Won', 'Lost', 'Tied', 'PF', 'PA', 'Rating', 'SOS'))
    sortedlist = sortDictByDesc(teamlist, "power")
    for team in sortedlist:
        print ('%-28s %4s %5s %5s %5s %5s %8.3f %6s' % (team['name'], team['won'], team['lost'], team['tied'], team['pf'], team['pa'], team['power'], team['sched_strength']))


def main():

    # Define the command line arguments
    infile   = sys.argv[1]
    sport    = sys.argv[2]
    #outfile  = sys.argv[3]

    # Initialize totalpoints and totalgames to 0.
    totalpoints = 0
    totalgames = 0

    # Create a list called Schedule. This list will contain dictionaries
    # of games.
    Schedule = []

    # Create a list called TeamList. This list will contain dictionaries
    # of teams.
    TeamList = []

    # Read in the scores file
    f = open(infile, 'r')
    try:
        fieldnames = ['date', 'team1', 'score1', 'team2', 'score2']
        gameReader = csv.DictReader(f, delimiter='|', fieldnames=fieldnames)
        for game in gameReader:
            Schedule.append(game)
    finally:
        f.close()

    # Get the total number of games played
    totalgames = len(Schedule)


    # Start reading the Schedule list. For each game, we will determine
    # the two teams involved, and get their information and update it.
    # We will also calculate the game_ratio and determine the expected
    # game_ratio so that we can provide a way to determine the performance
    # of each team in the game.
    for game in Schedule:
        # Calculate the total number of points scored
        totalpoints = totalpoints + int(game['score1']) + int(game['score2'])

        # Add the game_ratio to the game dictionary and calculate it
        game['game_ratio'] = calcGameRatio(int(game['score1']),
                                           int(game['score2']),
                                           sport)
        #team1info = lookupTeam(TeamList, game['team1'])
        #team2info = lookupTeam(TeamList, game['team2'])
        lookupTeam(TeamList, game['team1'])
        lookupTeam(TeamList, game['team2'])
        updateTeamStats(TeamList, game['team1'], int(game['score1']), \
                                  game['team2'], int(game['score2']))


    printSummary(totalgames, totalpoints)
    calcTeamRatings(TeamList, totalgames, Schedule)
    printRankings(TeamList)

if __name__ == "__main__":
    main()
