
txt_background = '''\

There is sometimes talk on TfTT about the verbosity of clueing style of a puzzle. Some
enjoy it, some don't and I (rv1) am normally in the latter camp.

As well as the enjoyment factor, I have always felt that verbosity adversely impacts my times and wondered if I could prove that. 

'''

txt_thanks = '''\

Clue data from https://timesforthetimes.co.uk/

NITCH data from https://times.xwdsnitch.link/

Thank you to TfTT and especially all the bloggers whose diligence in underlining or otherwise the
definition part of the clue enables the Defn part of this.

Particular thanks to Starstruck for providing back data for my WITCH and PITCH (personal NITCH)
over and above the usual excellence of the SNITCH.
'''

txt_conclusion = '''\
While there is clearly a connection between wordiness and difficulty that is hardly a surprise,
 it is easier to hide the wood if there are more trees.

There is a slight increase in wordiness on Fridays which tallies with SNITCH,
 setters know that wordiness increases difficulty.

As for my own prejudices, there is no evidence that it bothers me any more than anyone else so I should
 really stop whinging and learn to enjoy the variety. 

To a large extent all this was an excuse to learn a bit of Python and Plotly which I never had
cause to while working.
'''

txt_clue = '''\
The first and probably best chart. Downhill from here.
This measure has the highest R-squared value of all and it's hardly conclusive.

Splitting by Day (DoW) does not achieve much but I was enjoying myself.
You can click on the key to remove days.
There are always 2 audiences: those who understand the data and like it minimalist and
those who don't but like pretty colours and buttons to play with. (The sales team)
'''

txt_defn = '''\
Don't know about anyone else but I find it harder when the definition is a phrase rather than a single word.

BUT ... for some clues, notably CDs and DDs the whole clue is the definition. These are treated
separately here.

CD also includes a few where perhaps the blogger missed out the underlining entirely.
I fixed a few obvious outliers but not got time to check every one. 29345 and 29392 get a "See me".

CD/DDs are where DefnWC = ClueWC

Phrases where 1 < Defn < ClueWC 
'''

txt_solver_clue = '''\
PITCH is short for Personal NITCH. Not a term the official SNITCH uses.

WITCH is a solvers Wavelength ITCH, our score relative to everyone else.

Fails are not included in NITCH so here mine (in red) are given that day's NITCH so the
 red dots overwrite a grey NITCH one.
 
My fails simply increase with NITCH and, disappointingly,
 my WITCH actually goes down fractionally for the wordy ones 
'''

txt_solver_defn = '''\
This surprised me, I thought I would suffer from more of these.
It appears not, my WITCH barely twitches 
'''

txt_soln = '''\
Phrases being solutions with multiple words. I have always found multi-word answers easier to get a handle on.
'''

txt_solver_soln = '''\
I thought I would benefit more from lots of phrase solutions.
There is barely any correlation but my WITCH does decrease a tad with phrase count.
'''

txt_tech = '''\
Plotly Trendlines all use the OLS method, details can be seen by hovering over the line.
Most show very low R-squared values meaning that wordiness is not that good a determinant of NITCH.
Statisticians might suggest looking at the p-value. Maybe when the weather cools down.  

The data scraping and this app are all Python and the charts all plotly.express.
This is all very basic stuff but it is a sweetshop I would like to explore more.
The whole lot is stored in GitHub, there is a link at the top of the page if anyone is interested.

The presentation layer was never my forte so apologies for the clunkyness.
In particular I have tried to keep it mobile friendly so it looks a bit spaced out on desktop.
I could maybe use Columns intead of Tabs in desktop mode.
I got bogged down and bored by that bit TBH
'''