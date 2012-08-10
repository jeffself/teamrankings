teamrankings
============

A collection of apps for rankings sports teams.

rankings.py
-----------
Python app to rank a group of teams based on head to head matchups.

Usage
-----
    python rankings.py datafile sport

datafile is the name of the file containing the games. Replace sport with football,
basketball, or baseball.

The format of the data file is pipe-delimited containing the following data for each row:
    date|team1|team1_score|team2|team2|score
    Example:
    09/05/2005|Chicago|24|Miami|21

fbratings2.py
-------------
My first stab at rewriting my C app as a Python app. This is no longer maintained. I have it
here for reference while I work on rankings.py.

Usage
-----
    python fbratings.py datafile

The format of the data file is space-delimited containing the following data for each row:
    date team1 team1_score team2 team2_score
    Example:
    '09/05/2005  Chicago 24 Miami 21'

nflratings.c
------------
The original C version used in all my rankings. I can no longer compile it under OS X. It still
compiles under Linux however when compiled with the '-lm' option.

Usage
-----
    nflratings -i datafile -o outputfile
The format of the data file is space-delimited containing the following data for each row:
    date team1 team1_score team2 team2_score
    Example:
    '09/05/2005  Chicago 24 Miami 21'