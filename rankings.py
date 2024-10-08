"""Team Rankings application.

Synopsis
==========

    rankings.py [-sport] [-d '|'] scores.txt --output rankings.txt

Options
==========

The "-sport" option is either ``-football`` or ``-basketball`` to properly
normalize scores for these sports.  Most other sports don't require this
option.

A "-d" option specifies the file format. The default is CSV with column
titles.  A value of ``|`` (must be quoted to protect from the shell)
is a common alternative to specify pipe-delimited data with no column
titles.  In this case, the column order must be date, team1, score1,
team2, score2.

For scores extracted from web sites, a separate parser should be used
to create the required CSV file

A "--output" option specifies the output file. This option generates an
output file containing the rankings.

Arguments
===========

scores.txt is a CSV file.  The -d option allows different formats.

Each row in the file has results of a game:

    'date', 'team1', 'score1', 'team2', 'score2'

This is used to compute a "power" ranking that compares their total share
of points and games with a projected share.  The projection model is iterated
until it matches the actual outcomes.

rankings.txt is a text file that is optional. It is a generated text file
containing the generated rankings.

This is a Python 3.12 application.
"""

import math
import csv
from collections import namedtuple
import argparse
from dataclasses import dataclass, field
from typing import Callable, Literal
from pathlib import Path


# Raw input is a History record.
# Could be read via some kind of CSV reader, but numerous other
# formats are possible.

@dataclass(slots=True)
class History:
    """A record of a game.

    This is the raw data input for the program.  It's used to create
    instances of :class:`Game` which are used to calculate rankings.
    """
    date: str
    team1: str
    score1: int
    team2: str
    score2: int


@dataclass(slots=True)
class SportFactor:
    """Adjustments to normalize points into scoring opportunities.

    One instance of SportFactor is created based on run-time parameters.
    It's used to create instances of :class:`Game` from the raw
    :class:`History` data.
    """
    score_factor: float = 100.0
    max_score: float = 1.0

    def adjustScore(self, score):
        '''We adjust the score here to prevent a team from running up the
        score.
        '''

        golden = (1 + pow(5, 0.5)) / 2.0
        adjscore = score - ((score ** 2) / self.score_factor)
        adjusted_score = pow(adjscore / self.max_score, golden)
        return adjusted_score

    def gameRatio(self, score1, score2):
        '''The gameRatio method is used to determine the actual outcome
        of the game in a format that is equivalent to the expectedGameResult.

        We divide the adjusted score for each team by the greatest number of
        points a team can score at one time (i.e. 6 in football,
        3 in basketball, 1 in baseball and hockey). We add 1.0 in the
        numerator and 2.0 in the denominator to ensure that if the score is
        0 to 0, the function will return 0.5 instead of a divide by zero
        error.

        The winning team also gains an additional 1 point as a bonus
        whereas if the teams tie each team receives an additional 0.5 points.
        '''

        adjusted_score_1 = self.adjustScore(score1)
        adjusted_score_2 = self.adjustScore(score2)
        game_ratio = (adjusted_score_1 + 1.0) / (adjusted_score_1 + adjusted_score_2 + 2.0)
        if score1 > score2:
            game_ratio += 1.05
        elif score1 == score2:
            game_ratio += 0.5
        elif score1 < score2:
            pass # No adjustment for a loss
        else:
            raise Exception("Horrifying Design Error")
        return game_ratio * 0.5

@dataclass(slots=True)
class Football(SportFactor):

    """Football scoring adjustments."""
    score_factor: float = 500.0
    max_score: float = 6.0


@dataclass(slots=True)
class Basketball(SportFactor):

    """Basketball scoring adjustments."""
    score_factor: float = 750.0
    max_score: float = 3.0


@dataclass(slots=True)
class Team:

    """An individual team.  A name, plus a summary of wins, losses and points
    scored."""
    name: str
    won: int = 0
    lost: int = 0
    tied: int = 0
    pf: int = 0
    pa: int = 0
    hwon: int = 0
    hlost: int = 0
    htied: int = 0
    hpf: int = 0
    hpa: int = 0
    vwon: int = 0
    vlost: int = 0
    vtied: int = 0
    vpf: int = 0
    vpa: int = 0
    game_rate_accum: float = 0.0
    power: float = 100.0
    sched_strength: float = 0.0

    def updateStats(self, score: int, opponent: int) -> None:
        """
        For an individual game, record the win/loss and score for this game.
        """
        self.pf += score
        self.pa += opponent

        match score, opponent:
            case score, opponent if score > opponent:
                self.won += 1
            case score, opponent if score < opponent:
                self.lost += 1
            case score, opponent if score == opponent:
                self.tied += 1
            case _:
                raise Exception("Invalid scores: score and opponent must be non-negative integers")


@dataclass(slots=True)
class Game:

    """An individual game, hased on a History object read from a source.

    The game ratio is computed based on the sport.  Football and Basketball
    have a normalization factor applied.
    """
    default_sport = SportFactor()

    date: str
    team1: str
    score1: int
    team2: str
    score2: int
    game_ratio: float

    def __init__(self, history: History, sport: SportFactor):

        self.date = history.date
        self.team1 = history.team1.casefold()
        self.score1 = int(history.score1)
        self.team2 = history.team2.casefold()
        self.score2 = int(history.score2)
        self.game_ratio = sport.gameRatio(self.score1, self.score2)


def expectedGameResult(rating1, rating2, x):
    '''The expectedGameResult method is used to determine an expected
    outcome of a game.

    The expected outcome is determined by comparing
    the ratings of the two teams involved in the game. An expected ratio
    of 1.0 would mean that one team has a 100% chance of winning. An
    expected ratio of 0.5 would mean that each team has a 50% chance of
    winning.

    :param:`rating1` Team 1's rating.
    :param:`rating2` Team 2's rating.
    :param:`x` the "K factor" weighting, default is 10.0
    '''
    expected_ratio = (1 / (1 + pow(10, (rating2 - rating1) / x)))
    return expected_ratio


def updateTeamRating(teamlist, kfactor):
    for t in teamlist.values():
        t.power = t.power + \
            (kfactor *
                (t.game_rate_accum / (t.won + t.lost + t.tied)))


def calcTeamRatings(teamlist, totalgames, schedule):
    '''The calcTeamRatings method calculates each teams' power ratings.'''
    kfactor = 10.0
    tolerance = 1e-9
    std_dev_ratio = 1.0
    max_iterations = 25000
    std_dev_ratio_diff = 100.0
    old_std_dev_ratio = 1.0
    iterations = 0
    while ((std_dev_ratio_diff > tolerance) and (iterations < max_iterations)):
        old_std_dev_ratio = std_dev_ratio
        total_game_rate_accum = 0.0
        for t in teamlist.values():
            t.game_rate_accum = 0.0
        for g in schedule:
            team1_game_rating = teamlist[g.team1].game_rate_accum
            team1_rating = teamlist[g.team1].power
            team2_game_rating = teamlist[g.team2].game_rate_accum
            team2_rating = teamlist[g.team2].power
            team1_game_rating = team1_game_rating + g.game_ratio - \
                expectedGameResult(team1_rating, team2_rating, kfactor)
            team2_game_rating = team2_game_rating + 1 - g.game_ratio - \
                (1 - expectedGameResult(team1_rating, team2_rating, kfactor))
            teamlist[g.team1].game_rate_accum = team1_game_rating
            teamlist[g.team2].game_rate_accum = team2_game_rating
            if team1_game_rating > team2_game_rating:
                total_game_rate_accum = total_game_rate_accum + team1_game_rating
            else:
                total_game_rate_accum = total_game_rate_accum + team2_game_rating
        # Calculate grate standard deviation
        std_dev_ratio = math.sqrt(((
            total_game_rate_accum ** 2) / totalgames))
        std_dev_ratio_diff = (old_std_dev_ratio - std_dev_ratio) ** 2
        iterations = iterations + 1
        # Revise ratings
        updateTeamRating(teamlist, kfactor)
    if (iterations > max_iterations):
        print("Fatal error: Game ratios aren't converging")
    else:
        print('The scores were examined {} times.'.format(iterations))


def printSummary(total_games, total_points):
    avg_pts_game = float(total_points / total_games / 2)
    print('The total number of games played is {}'.format(total_games))
    print('The total number of points scored is {}'.format(total_points))
    print('The average number of points scored per team per game is {0:.3f}'
          .format(avg_pts_game))


def sortDictByPower(teamlist):
    sorted_list = sorted(teamlist, key=lambda t: t.power, reverse=True)
    return sorted_list


def printRankings(args, teamlist):
    '''The printRankings method returns the calculated rankings in text format and also saves to a CSV file'''
    fmt = "{0.name:40s} {0.won:4d} {0.lost:5d} {0.tied:5d} " + \
          "{0.pf:5d} {0.pa:5d} {0.power:8.3f}"
    sorted_list = sortDictByPower(teamlist.values())

    for t in sorted_list:
        t.name = t.name.upper()

    # Export in text format using Pathlib
    if args.output:
        output_path = Path(args.output)
        with output_path.open('w') as f:
            f.write('{:>4s} {:>40s} {:>4s} {:>5s} {:>5s} {:>5s} {:>5s} {:>8s}'
                    .format('Rank', '', 'Won', 'Lost', 'Tied', 'PF', 'PA', 'Rating'))
            f.write('\n')
            for team in sorted_list:
                f.write('{0:4d}'.format(sorted_list.index(team) + 1) + ' ' +
                        fmt.format(team) + '\n')
    else:
        # Print to console in text format
        print('{:>4s} {:>40s} {:>4s} {:>5s} {:>5s} {:>5s} {:>5s} {:>8s}'
              .format('Rank', '', 'Won', 'Lost', 'Tied', 'PF', 'PA', 'Rating')
              )
        for team in sorted_list:
            print('{0:4d}'.format(sorted_list.index(team) + 1) + ' ' +
                  fmt.format(team))

    # Automatically create CSV filename based on output filename using Pathlib
    csv_filename = output_path.with_suffix('.csv') if args.output else Path('rankings.csv')
    with csv_filename.open('w', newline='') as csvfile:
        fieldnames = ['Rank', 'Team', 'Won', 'Lost', 'Tied', 'PF', 'PA', 'Rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rank, team in enumerate(sorted_list, start=1):
            writer.writerow({
                'Rank': rank,
                'Team': team.name,
                'Won': team.won,
                'Lost': team.lost,
                'Tied': team.tied,
                'PF': team.pf,
                'PA': team.pa,
                'Rating': f"{team.power:.3f}"
            })

    print(f"Rankings have been exported to {csv_filename} as well.")


class HistoryReader:
    """Abstract superclass for History readers."""

    def __init__(self, source):
        self.source = source

    def __iter__(self):
        """Yield History instances from the source."""
        raise NotImplementedError("Subclasses must implement this method.")


class CSVHistoryReader(HistoryReader):

    """Create History instances from CSV files with proper column names
    in the first row.

    Column names must include: 'date', 'team1', 'score1', 'team2', 'score2'
    in any order.
    """
    def __init__(self, source):
        super().__init__(source)
        self.reader = csv.DictReader(self.source)

    def __iter__(self):
        for row in self.reader:
            yield History(**row)


class PipeFormatHistoryReader(HistoryReader):

    """Create History instances from pipe-formatted files.

    In this case, column names are assumed which **must** match the
    :class:`History` class fields.

    Specifically: 'date', 'team1', 'score1', 'team2', 'score2'.
    """
    def __init__(self, source):
        super().__init__(source)
        self.reader = csv.DictReader(source, delimiter='|',
                                     fieldnames=['date', 'team1', 'score1','team2', 'score2'])

    def __iter__(self):
        for row in self.reader:
            yield History(**row)


def load(source: HistoryReader, sport: Callable[[int, int], float]) -> tuple[int, int, dict[str, Team]]:
    """Load the TeamList and some totals.

    :param:`source` is an iterable source of History instances.  Usually
        an instance of :class:`HistoryReader`.
    :param:`sport` is an instance of :class:`SportFactor`.
    """
    # Initialize totalpoints and totalgames to 0.
    total_points = 0
    total_games = 0

    # Create a list called Schedule. This list will contain Game instances.
    Schedule = []

    # Create a mapping from team name to Team instance.
    # of teams.
    TeamList = {}

    # Start reading the Schedule list. For each game, we will determine
    # the two teams involved, and get their information and update it.
    # We will also calculate the game_ratio and determine the expected
    # game_ratio so that we can provide a way to determine the performance
    # of each team in the game.
    for history in source:

        # Create the Game, including the game_ratio, based on History.
        game = Game(history, sport)

        # Add the game to the Schedule.
        Schedule.append(game)

        # Calculate the total number of points scored.
        total_points = total_points + game.score1 + game.score2

        # Create the teams, if they didn't already exist.
        team1 = TeamList.setdefault(game.team1, Team(game.team1))
        team2 = TeamList.setdefault(game.team2, Team(game.team2))

        #Update the won-lost-tied record and pts
        #scored and pts allowed for each of the two teams involved in a game.
        team1.updateStats(game.score1, game.score2)
        team2.updateStats(game.score2, game.score1)

    # Get the total number of games played.
    total_games = len(Schedule)

    # Calculate the rankings.
    calcTeamRatings(TeamList, total_games, Schedule)

    # Return values for display.
    return total_games, total_points, TeamList


def report(args, totalgames, totalpoints, TeamList):
    """Produce the two printed reports."""
    printSummary(totalgames, totalpoints)
    printRankings(args, TeamList)


def processRankings(args, source, sport):
    """The default command-line app: load and report."""

    # Step 1: Load the data from the file, compute the rankings.
    total_games, total_points, TeamList = load(source, sport)

    # Step 2: Print a report.
    report(args, total_games, total_points, TeamList)


def main():
    """Parse command-line arguments, run the :func:`process_rankings` function.
    """
    parser = argparse.ArgumentParser(description='Rankings')
    parser.add_argument('-football', dest='sport', action='store_const',
                        const=Football())
    parser.add_argument('-basketball', dest='sport', action='store_const',
                        const=Basketball())
    parser.add_argument('-d', dest='format', action='store')
    parser.set_defaults(sport=SportFactor())
    parser.add_argument('file_list', metavar='History File', type=open,
                        nargs='+', help='Files with Game History')
    parser.add_argument('--output', required=False)
    parser.add_argument('output_file', metavar='Rankings File', type=open,
                        nargs='?', help='The rankings file')
    args = parser.parse_args()

    match args.format:
        case None:
            reader_class = CSVHistoryReader
        case '|':
            reader_class = PipeFormatHistoryReader
        case _:
            raise Exception("Unknown -d {0}".format(args.format))
        
    for source in args.file_list:
        reader = reader_class(source)
        processRankings(args, reader, args.sport)


if __name__ == "__main__":
    main()
