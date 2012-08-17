"""Team Rankings unit test case(s).

These are just two super-simplistic unit test cases
for the rankings.py application.

..  todo:: Write more tests: Team, Game, etc.
"""
import unittest
import sys
import io

import rankings

class Test_Reports( unittest.TestCase ):
    def setUp( self ):
        with open("scores1979.txt","r") as source:
            reader= rankings.PipeFormatHistoryReader( source )
            self.totalgames, self.totalpoints, self.TeamList = rankings.load( reader, rankings.Football() )
    def test_should_produce_summary( self ):
        self.assertEqual( 159, self.totalgames )
        self.assertEqual( 4396, self.totalpoints )
        self.assertEqual( 73, len(self.TeamList) )
        sortedlist = rankings.sortDictByPower(self.TeamList.values())

        # Southampton                     4     0     0   107    14   67.609
        self.assertEqual( 'Southampton', sortedlist[0].name )
        self.assertEqual( 4, sortedlist[0].won )
        self.assertEqual( 0, sortedlist[0].lost )
        self.assertEqual( 0, sortedlist[0].tied )
        self.assertEqual( 107, sortedlist[0].pf )
        self.assertEqual( 14, sortedlist[0].pa )
        self.assertAlmostEqual( 67.90649022216157, sortedlist[0].power )

    def test_should_format_summary( self ):
        output_report = io.StringIO()
        sys.stdout= output_report
        rankings.printRankings( self.TeamList )
        with open("rankings_1979.txt","r") as captured:
            for e, a in  zip( (l.rstrip() for l in captured.readlines()),
                    output_report.getvalue().splitlines() ):
                self.assertEqual( e, a )

class TestSportFactor( unittest.TestCase ):
    def setUp( self ):
        self.sf= rankings.SportFactor()
    def test_should_normalize_score( self ):
        self.assertAlmostEqual( 1-(1**2)/100, self.sf.adjustScore( 1 ) )
        self.assertAlmostEqual( 6-(6**2)/100, self.sf.adjustScore( 6 ) )
        self.assertAlmostEqual( 12-(12**2)/100, self.sf.adjustScore( 12 ) )
    def test_should_compute_game_ratio( self ):
        a1, a2 = (1-(1**2)/100)**2, (2-(2**2)/100)**2
        self.assertAlmostEqual( (a1+1)/(a1+a2+2)/2, self.sf.gameRatio(1,2) )
        a1, a2 = (2-(2**2)/100)**2, (2-(2**2)/100)**2
        self.assertAlmostEqual( ((a1+1)/(a1+a2+2)+.5)/2, self.sf.gameRatio(2,2) )
        a1, a2 = (2-(2**2)/100)**2, (1-(1**2)/100)**2,
        self.assertAlmostEqual( ((a1+1)/(a1+a2+2)+1)/2, self.sf.gameRatio(2,1) )

class TestFootballSportFactor( unittest.TestCase ):
    def setUp( self ):
        self.sf= rankings.Football()
    def test_should_normalize_score( self ):
        self.assertAlmostEqual( 1-(1**2)/250, self.sf.adjustScore( 1 ) )
        self.assertAlmostEqual( 6-(6**2)/250, self.sf.adjustScore( 6 ) )
        self.assertAlmostEqual( 12-(12**2)/250, self.sf.adjustScore( 12 ) )
    def test_should_compute_game_ratio( self ):
        a1, a2 = ((1-(1**2)/250)/6)**2, ((2-(2**2)/250)/6)**2
        self.assertAlmostEqual( (a1+1)/(a1+a2+2)/2, self.sf.gameRatio(1,2) )
        a1, a2 = ((2-(2**2)/250)/6)**2, ((2-(2**2)/250)/6)**2
        self.assertAlmostEqual( ((a1+1)/(a1+a2+2)+.5)/2, self.sf.gameRatio(2,2) )
        a1, a2 = ((2-(2**2)/250)/6)**2, ((1-(1**2)/250)/6)**2,
        self.assertAlmostEqual( ((a1+1)/(a1+a2+2)+1)/2, self.sf.gameRatio(2,1) )

class TestBasketballSportFactor( unittest.TestCase ):
    def setUp( self ):
        self.sf= rankings.Basketball()
    def test_should_normalize_score( self ):
        self.assertAlmostEqual( 80-(80**2)/750, self.sf.adjustScore( 80 ) )
        self.assertAlmostEqual( 90-(90**2)/750, self.sf.adjustScore( 90 ) )
        self.assertAlmostEqual( 100-(100**2)/750, self.sf.adjustScore( 100 ) )
    def test_should_compute_game_ratio( self ):
        a1, a2 = ((80-(80**2)/750)/3)**2, ((90-(90**2)/750)/3)**2
        self.assertAlmostEqual( (a1+1)/(a1+a2+2)/2, self.sf.gameRatio(80,90) )
        a1, a2 = ((80-(80**2)/750)/3)**2, ((80-(80**2)/750)/3)**2
        self.assertAlmostEqual( ((a1+1)/(a1+a2+2)+.5)/2, self.sf.gameRatio(80,80) )
        a1, a2 = ((90-(90**2)/750)/3)**2, ((80-(80**2)/750)/3)**2
        self.assertAlmostEqual( ((a1+1)/(a1+a2+2)+1)/2, self.sf.gameRatio(90,80) )

if __name__ == "__main__":
    unittest.main()