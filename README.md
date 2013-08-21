teamrankings
============

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
titles.  In this case, the column order must be date, team1, score1, team2, score2.

For scores extracted from web sites, a separate parser should be used
to create the required CSV file

A "--output" option specifies the output file. This option generates an output file
containing the rankings.

Arguments
===========

scores.txt is a CSV file.  The -d option allows different formats.

Each row in the file has results of a game:

    'date', 'team1', 'score1', 'team2', 'score2'

This is used to compute a "power" ranking that compares their total share
of points and games with a projected share.  The projection model is iterated
until it matches the actual outcomes.

Requirements
============

This application has been tested and runs on Python 3.3. For any other version of Python, your mileage may vary.

Data Files
==========

I have existing data files for pro football, college football, and Virginia high school football
on Github now. Some are in space-delimited format and others have been migrated to pipe-delimited
format.

* [Pro Football scores](https://github.com/jeffself/profootballscores)
* [College Football scores](https://github.com/jeffself/collegefootballscores)
* [Virginia High School Football scores](https://github.com/jeffself/vahsfbscores)