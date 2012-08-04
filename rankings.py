import sys
import string
import math
import csv


def totalPtsGame(score1, score2):
    '''The totalPtsGame method returns the total points scored in the
    game.

    '''
    return score1 + score2

def avgPtsGame(total_points, total_games):
    '''The avgPtsGame method returns the average points scored per
    team per game.

    '''
    return float(total_points / total_games / 2)

def adjustScore(score):
    '''We adjust the score here to prevent a team from running up the
    score.
    '''
    adjScore = score - (score * score)/250.0
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

    adjScore1 = pow((adjustScore(score1))/max_score,2)
    adjScore2 = pow((adjustScore(score2))/max_score,2)
    gameRatio = (adjScore1 + 1.0) / (adjScore1 + adjScore2 + 2.0)
    if score1 > score2:
        gameRatio = gameRatio + 1.0
    else:
        if score1 == score2:
            gameRatio = gameRatio + 0.5
    return gameRatio * 0.5

def addTeam (teamlist, name):
    '''The addTeam function is used to add a team to the teamlist.  All
    values are set to 0 except for the rating which is set to 50.0.

    '''
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

def lookupTeam (teamlist, teamname):
    '''The lookupTeam function is used to look up a team in the teamlist.
    If the team is not located, then we call the addTeam function.

    '''
    for row in teamlist:
        if teamname == row['name']:
            break
    else:
        addTeam (teamlist, teamname)

def updateTeamStats (teamlist, team1, score1, team2, score2):
    '''The updateTeamStats function updates the won-lost-tied record and pts
    scored and pts allowed for each of the two teams involved in a game.

    '''
    lookupTeam (teamlist, team1)
    lookupTeam (teamlist, team2)
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

def main():
    '''Create a list called Schedule.  This list will contain
    dictionaries of games.

    '''
    Schedule = []

    '''Create a list called TeamList. This list will contain
    dictionaries of teams.

    '''
    TeamList = []

    '''Read in the scores file'''
    f = open(sys.argv[1], 'r')
    try:
        gameReader = csv.reader(f, delimiter='|')
        for game in gameReader:
            g = {}
            g['date'], g['team1'], g['score1'], g['team2'], g['score2'] = game
            g['score1'] = int(g['score1'])
            g['score2'] = int(g['score2'])
            Schedule.append(g)
    finally:
        f.close()


    '''Initialize totalpoints and totalgames to 0.'''
    totalpoints = 0
    totalgames = 0

    '''Get the sport from argument 2 on the command line'''
    sport = sys.argv[2]

    for g in Schedule:
        '''We're getting the total points and the total games played'''
        totalpoints = totalpoints + g['score1'] + g['score2']
        totalgames = totalgames + 1

        '''Add the field ratio to the game dictionary and call
           calcGameRatio to get the result
        '''
        g['ratio'] = calcGameRatio(g['score1'], g['score2'], sport)

        '''Update the stats for each of the game's participants'''
        updateTeamStats(TeamList, g['team1'], g['score1'], g['team2'], g['score2'])

if __name__ == "__main__":
    main()
