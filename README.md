teamrankings
============

Python app to rank a group of teams based on head to head matchups.

rankings.py
-----------

Usage
-----
    python rankings.py datafile sport

datafile is the name of the file containing the games. Replace sport with football,
basketball, or baseball.
The format of the data file is pipe-delimited containing the following data for each row:
date|team1|team1_score|team2|team2|score
Example:
09/05/2005|Chicago|24|Miami|21

To use the old python app, fbratings2.py, type the following at the command line:
python fbratings.py datafile
The format of the data file is space-delimited containing the following data for each row:
date team1 team1_score team2 team2_score
Example:
'09/05/2005  Chicago 24 Miami 21'

To use the C version, nflratings.c, you must compile it and run it at the command line:
nflratings -i datafile -o outputfile