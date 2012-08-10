/* Football Ranking System
 *
*/

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Default files if no command line options given */
#define DEFAULT_INFILE "games.txt"
#define DEFAULT_OUTFILE "rank.txt"

/* Constants */

const AdjDen  = 250.0;  /* This is used in the AdjustPts calculation. */

/* This is a Game struct */
struct Game {
   struct Team *visitor, *home;
   int vscore, hscore;
   int location;
   double ratio;
   struct Game *next;
};

/* This is a Team struct */
struct Team {
   char *name;
  /* Team's record and points scored and points allowed */
   int won, lost, tied, pf, pa, schedplace;
   int hwon,hlost,htied,hpf,hpa;	/* Home game stats */
   int vwon,vlost,vtied,vpf,vpa;	/* Road game stats */
   double grate;  /* Ratio - Expected Ratio */
  /* Team's rating and how fast its changing */
   double rating;
  /* Schedule strength */
   double sched;
   struct Team *next;
};

/* Function Prototypes */
void argError();
char *chmalloc(int size);
void readGames(char *infile);
struct Team *lookup_team(char *name);
struct Team *new_team(char *name);
void calcRatio();
void calcSchedStrength();
double gameRatio(struct Game *g);
double adjPoints(int);
void calcRating(char *outfile);
void displayRankings(char *outfile);
void calcCompRecord();
void printHeadings(char *outfile);

struct Team *teamlist = NULL;
struct Game *gamelist = NULL;

int main(int argc, char *argv[])
{
   int i;
   char *arg, *infile, *outfile;
   
   infile = outfile = 0;

   /* Parse commandline arguments */
   for (i = 1; i < argc; i++) {
      arg = argv[i];
      if (*arg == '-') {
         if (!*(arg + 1))
            argError();
         if (!(arg + 2))
            argError();
         switch (arg[1]) {
         case 'i':
            if (argc > (i + 1))
               infile = strdup(argv[i+1]);
            else
               argError();
            break;
         case 'o':
            if (argc > (i + 1))
               outfile = strdup(argv[i + 1]);
            else
               argError();
            break;
         default:
            argError();
            break;
         }
      }
   }
   if (!infile)
      infile = strdup(DEFAULT_INFILE);
   if (!outfile)
      outfile = strdup(DEFAULT_OUTFILE);
   
   readGames(infile);
   calcRatio();
   calcRating(outfile);
   calcSchedStrength();
   printHeadings(outfile);
   displayRankings(outfile);
   calcCompRecord();

   exit(0);
}

void argError()
{
   fprintf(stderr, "Run the program with the following command: nflratings [-i inputfile] [-o outputfile]\n" );
   exit(1);
}

char *chmalloc(int size)
{
   char *buffer;
   buffer = calloc(1, size);
   if (!buffer) {
      fprintf(stderr, "Fatal error: could not allocate %i bytes\n" , size);
      exit(1);
   }
}

void readGames(char *infile)
{
   char *buffer;
   char *ptr, *ptr2;
   char ch;
   int whichteam;
   char *name;			/* Name of the team we're parsing */
   int score;	/* Score of the team we're parsing */
   int lineno = 0;		/* Count the line number */
   struct Game *g;
   int totalgames = 0;
   int totalpoints = 0;
   int i;
   
   /* Open the input file */
   FILE *data;
   data = fopen(infile, "r");
   if (!data) {
      fprintf(stderr, "** Can't open the input file** %s\n" , infile);
      exit(1);
   }
   
   /* Read the games */
   fprintf(stderr, "Reading %s\n" , infile);
   while (!feof(data)) {
      lineno++;
      buffer = chmalloc(256);
      fgets(buffer, 255, data);
      g = (struct Game *) chmalloc(sizeof(struct Game));
         
      /* Check for blank line or commented line */
      ptr = buffer -1;
      while ((ch = *++ptr) && *ptr <= '!');
      if (!ch || ch == '#') {
         continue;
      }

      /* Uncomment the following lines if date field is on each line of data */
      /* Skip date field */
      for (i=0; i<=9; i++) { 
        ptr++; 
      } 
  
      /* Point to first non-whitespace character */
      ptr--;
      for (whichteam = 1; whichteam <=2; whichteam++) {
         /* Find where name starts */
         while ((ch = *++ptr) && *ptr <= '!');
         if (!ch) {
            whichteam = 0;		/* We didn't find a name */
            break;
         }
         name = ptr;	/* Name starts here */
         
         /* Now find where name ends */
         do {
            while ((ch = *++ptr) > ' ');
            if (!*ptr) {
               whichteam = 0;	/* No score found...surrender */
               break;
            }
            ptr2 = ptr;		/* Name might end here */
            while ((ch = *++ptr) && ch <= ' ');
         }
         while (ch < '0' || ch > '9');		/* Stop at digit */
         *ptr2 = '\0';		/* The name ends here */
         
         /* Now find the team's score */
         score = 0;
         do {
            score = 10 * score +ch - '0';
            ch = *++ptr;
         }
         while (ch >= '0' && ch <= '9');
         
         /* Set values for appropriate team */
         if (whichteam == 1) {
            g->visitor = lookup_team(name);
            if (!g->visitor)
               g->visitor = new_team(name);
            g->vscore = score;
         } else if (whichteam == 2) {
            g->home = lookup_team(name);
            if (!g->home)
               g->home = new_team(name);
            g->hscore = score;
         }
      }
            
      /* Look for location information */
      while ((ch = *++ptr) < '!')
      {
        g->location = (ch == '0' | ch == 'n') ? 0 : 1;
      }
      
      /* Continue with rest of line */
      while ((ch = *++ptr) && ch < '!')
      {
         if (ch)
            continue;
      }
      
      /*  Calculate total points.  This only works if everything else worked. */
      totalpoints += g->vscore + g->hscore;
      totalgames++;
      g->next = gamelist;
      gamelist = g;
      free(buffer);
   }
   
   /* Print summary stats */
   printf("%i games successfully read\n" , totalgames);
   printf("Average points per team per game: %f\n" , \
       (double) totalpoints / totalgames / 2);

   fclose(data);
}

struct Team *lookup_team(char *name)
{
   struct Team *t = teamlist;
   
   /* Teamlist should be alphabetically sorted, so this works */
   while (t && strcmp(t->name, name) <= 0) {
      if (!strcmp(t->name, name))
         return t;
      t = t->next;
   }
   return NULL;
}

struct Team *new_team(char *name)
{
   struct Team *new;
   struct Team *t = teamlist, *prev = NULL;
   
   /* Initialize the new team */
   new = (struct Team *) chmalloc(sizeof(struct Team));
   new->name = strdup (name);
   new->won = new->lost = new->tied = new->pf = new->pa =
              new->sched = new->grate = new->hwon = new->hlost =
              new->htied = new->hpf = new->hpa = new->vwon = 
              new->vlost = new->vtied = new->vpf = new->vpa = 0;
   new->rating = 50.0;
 
   /* Stick team into sorted list */
   t = teamlist;
   while (t && strcmp(t->name, new->name) < 0) {
      prev = t;
      t = t->next;
   }
   if (prev) {
      if (prev->next)
         new->next = prev->next;
      prev->next = new;
   } else {
      /* It must have been first alphabetically */
      new->next = teamlist;
      teamlist = new;
   }
   return new;
}
  
/* Run once to determine game ratios */
void calcRatio()
{
   struct Team *t;
   struct Game *g;
   int games = 0;

   fprintf(stderr, "Calculating game stats\n" );

   /* Calculate team statistics and gameRatio difference */
   for (g = gamelist; g; g = g->next) {
      g->ratio = gameRatio(g);

      if (g->vscore > g->hscore) {
         g->visitor->won++;
         g->home->lost++;
         if (g->location == 1) {
         	g->home->hlost++;
         	g->visitor->vwon++;
         }
      } else if (g->vscore < g->hscore) {
         g->visitor->lost++;
         g->home->won++;
		 if (g->location == 1) {
			 g->home->hwon++;
   	      g->visitor->vlost++;
   	  }
      } else {
         g->visitor->tied++;
         g->home->tied++;
         if (g->location == 1) {
         	g->home->htied++;
         	g->visitor->vtied++;
         }
      }

      g->visitor->pf += g->vscore;
      g->visitor->pa += g->hscore;
      g->home->pf += g->hscore;
      g->home->pa += g->vscore;
      if (g->location == 1) {
      	g->home->hpf += g->hscore;
      	g->home->hpa += g->vscore;
      	g->visitor->vpf += g->vscore;
      	g->visitor->vpa += g->hscore;
      }
      games++;
   }   
}

double gameRatio(struct Game *g)
{
   double result;
   
   result = ((adjPoints(g->vscore)/6) * (adjPoints(g->vscore)/6) + 1.0)/
          ((adjPoints(g->vscore)/6) * (adjPoints(g->vscore)/6) + (adjPoints(g->hscore)/6) *
	  (adjPoints(g->hscore)/6) + 2.0);
   
   if (g->vscore > g->hscore)
      result += 1;
   else if (g->vscore == g->hscore)
      result += .5; 
   return (result * .5);

}

double adjPoints(int score)
{
   double newscore;
   
   newscore = (double) score - (double)(score * score)/400;
   return (newscore);
}

void calcRating(char *outfile)
{
   struct Game *g;
   struct Team *t;
   double v_expected;       /* Expected ratio of visiting team*/
   double sum_grate;
   double stdDevRatio;
   double stdDevRatioDiff;
   double oldstdDevRatio;
   double tolerance = 1e-9;
   double Kfactor = 10.0;
   
   int max_iterations = 25000;
   int iterations = 0;
   int teams = 0, games = 0;
   int i = 0;                 /* Iterations */

   stdDevRatio = 1.0;
   stdDevRatioDiff = 100.0;    /* Set to any number > tolerance */
   oldstdDevRatio = 1.0;
   printf("Calculating ratings\n" );
   while ((i < max_iterations) && (stdDevRatioDiff > tolerance)) {
      games = 0;
      oldstdDevRatio = stdDevRatio;
      sum_grate = 0.0;
      iterations += 1;
      /* Initialize team ratios */
      teams = 0;
      for (t = teamlist; t; t = t->next) {
         t->grate = 0.0;
         teams++;
      }

      /* Calculate expected ratio */
	for (g = gamelist; g; g = g->next) {
		v_expected =( 1/ (1 + pow( 10,(g->home->rating - g->visitor->rating) / Kfactor)));
		g->visitor->grate += (g->ratio - v_expected);
		g->home->grate += (1 - g->ratio - (1 - v_expected));
		if (g->visitor->grate > g->home->grate)
         	sum_grate += g->visitor->grate;
		else
		 	sum_grate += g->home->grate;
		games++;
	}
      
      /* Calculate grate standard deviation */
      stdDevRatio = sqrt((sum_grate*sum_grate/games));
      stdDevRatioDiff = pow(oldstdDevRatio - stdDevRatio,2);
      if (!(i % 250)) {   /* Update the progress */
         printf("Game ratio standard deviation: %f\n", stdDevRatio);
      }
      
      /* Calculate team ratings */
      teams = 0;
      for (t = teamlist; t; t = t->next) {
         t->rating += Kfactor * (t->grate / (t->won + t->lost + t->tied));
         teams++;
      }
      i++;
   }
   if (i > max_iterations) {
      /* displayRankings(outfile); */
      printf("Fatal error: Game ratios aren't converging.\n" );
   } else {
      printf("Congratulations!  Game Ratios have converged!\n" );
      }
   printf("The program ran through the scores %i times!\n", iterations);
}

void calcCompRecord()
{
   struct Game *g;
   struct Team *t;
   int compwins = 0;
   int complosses = 0;
   float comppct;

   for (g=gamelist; g; g = g->next) {
      if ((g->visitor->rating > g->home->rating) && (g->vscore > g->hscore)) 
         compwins++;
      else if ((g->home->rating > g->visitor->rating) && (g->hscore > g->vscore))
         compwins++;
      else
         complosses++;
   }
   comppct = ((float)compwins/(compwins+complosses));
   printf("Computer Performance: %d-%d %.3f\n", compwins, complosses, comppct);
}

void calcSchedStrength()
{
   struct Game *g;
   struct Team *t;
   struct Team *sortp, **sortpp;
   int place;
   double last_rating = 1 / 0.0;
   
   for (g=gamelist; g; g = g->next) {
      g->visitor->sched += g->home->rating;
      g->home->sched += g->visitor->rating;
   }
   
   for (t=teamlist; t; t = t->next) {
      t->sched /= (t->won + t->lost + t->tied);
   }

   /* sort the teams by schedule strength*/
   t = teamlist;
   teamlist = NULL;
   while (t)  {
      sortpp = &teamlist;
      while ((sortp = *sortpp) && (t->sched < sortp->sched))
         sortpp = &(sortp->next);
      *sortpp = t;
      t = t->next;
      (*sortpp)->next = sortp;
   }

   /* Check for even rankings */
   place = 0;
   for (t = teamlist; t; t = t->next) {
      place++;
      if (last_rating != t->sched) {
         t->schedplace = place;
         last_rating = t->sched;
      } else
      	    t->schedplace = place - 1;
   }
}
   
void displayRankings(char *outfile)
{
   int place, ranking;
   struct Team *sortp, **sortpp;
   struct Team *t;
   double last_rating = 1 / 0.0;

   /* Open the file */
   FILE *rank;
   rank = fopen(outfile, "a");
   if (!rank) {
      fprintf(stderr, "Fatal error:  could not write to file %s\n" , outfile);
      exit(1);
   }

   /* sort the teams */
   t = teamlist;
   teamlist = NULL;
   while (t)  {
      sortpp = &teamlist;
      while ((sortp = *sortpp) && (t->rating < sortp->rating))
         sortpp = &(sortp->next);
      *sortpp = t;
      t = t->next;
      (*sortpp)->next = sortp;
   }

   /* Check for even rankings and write to file */
   place = 0;
   for (t = teamlist; t; t = t->next) {
      place++;
      if (last_rating != t->rating) {
         ranking = place;
         last_rating = t->rating;
      }
      fprintf(rank, "%3i %-20.20s %2i %2i %2i %4i %4i %7.3f %7.3f (%3i) %2i %2i %2i %4i %4i %4i %2i %2i %4i %4i\n" ,
                  ranking, t->name, t->won, t->lost, t->tied, t->pf,
                  t->pa, t->rating, t->sched, t->schedplace, t->hwon, t->hlost,
                  t->htied, t->hpf, t->hpa, t->vwon, t->vlost,
                  t->vtied, t->vpf, t->vpa);
   }
   fclose(rank);
   return;
}

void printHeadings(char *outfile) {
	FILE *rank;
	rank = fopen(outfile,"w");
	fprintf(rank, "%33s %10s %32s %20s\n"," ", "Overall", "Home", "Away");
	fprintf(rank, \
           "%3s %-20s %2s %2s %2s %4s %4s %7s %7s %8s %2s %2s %4s %4s %4s %2s %2s %4s %4s\n"  ,
           "Rnk", "Team", "W", "L", "T", "PF", "PA", "RATE", "SOS", "W", "L", "T", "PF", "PA", "W", "L", "T", "PF", "PA");
	fprintf(rank, \
           "%3s %-20s %2s %2s %2s %4s %4s %7s %7s %8s %2s %2s %4s %4s %4s %2s %2s %4s %4s\n"  , 
           "---", "----", "-", "-", "-", "--", "--", "------", "------", "-", "-", "-", "--", "--", "-", "-", "-", "--", "--");
	fclose(rank);
	return;
}
