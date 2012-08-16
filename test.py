import unittest
import sys
import io

import rankings


class Test_Reports( unittest.TestCase ):
    def test_should_produce_summary( self ):
        with open("scores1979.txt","r") as source:
            totalgames, totalpoints, TeamList = rankings.load( source, 'football' )
        self.assertEqual( 159, totalgames )
        self.assertEqual( 4396, totalpoints )
        self.assertEqual( 73, len(TeamList) )
        sortedlist = rankings.sortDictByDesc(TeamList, "power")

        # Southampton                     4     0     0   107    14   67.609
        self.assertEqual( 'Southampton', sortedlist[0]['name'] )
        self.assertEqual( 4, sortedlist[0]['won'] )
        self.assertEqual( 0, sortedlist[0]['lost'] )
        self.assertEqual( 0, sortedlist[0]['tied'] )
        self.assertEqual( 107, sortedlist[0]['pf'] )
        self.assertEqual( 14, sortedlist[0]['pa'] )
        self.assertAlmostEqual( 67.60850400936893, sortedlist[0]['power'] )

    def test_should_format_summary( self ):
        with open("scores1979.txt","r") as source:
            totalgames, totalpoints, TeamList = rankings.load( source, 'football' )
        output_report = io.StringIO()
        sys.stdout= output_report
        rankings.printRankings( TeamList )
        with open("rankings_1979.txt","r") as captured:
            for e, a in  zip( (l.rstrip() for l in captured.readlines()),
                    output_report.getvalue().splitlines() ):
                self.assertEqual( e, a )

if __name__ == "__main__":
    unittest.main()