#!/home/harvey/Python/venvs/rv python

# For print output redirection
from contextlib import redirect_stdout
# Why does just import datetime not work?
from datetime import datetime, timedelta
# time for sleep. Zzzzzzz
import time
# Regular expressions lib
# https'://docs.python.org/3/library/re.html
import re
# HTTP for humans
# https://pypi.org/project/requests/
import requests
# Beautiful Soup web scraping lib
# https'://pypi.org/project/beautifulsoup4/
import bs4
# Save data locally in sqlite
import sqlite3
# pathlib to find db file
from pathlib import Path
# My Crossword classes
from crossword import Puzzle, Clue
# My http scraping lib
import scrape

# Somewhere to store the clue info as we extract it

# Constants
dbpath = Path('assets/xword.db')

urltftt = "https://timesforthetimes.co.uk/"
urlpnum = urltftt + "?s={}"
urlpdat = urltftt + "{}/{}/{}"

# Globals
# crossword.Puzzle
oPuzzle = None
# HTTP session
session = requests.session()
# No need to keep reopening DB connection 
conn = sqlite3.connect(dbpath)

# Functions

# Get the HTML for a puzzle blog page
# url = "https://timesforthetimes.co.uk/times-cryptic-29538-sat-9-may-2026-nine-part-harmony"
   
# Use Search facility to find by puzzle # and/or Date
# This page is built by Wordpress, not by TfTT bloggers so should be reliable
def getpuzzleurl(puzzleno = None, puzzledate = None):
    
    puzzleurl = None
    #print("getpuzzleurl " + str(puzzleno))
    urlsearch = None
    
    # Params are constructed by us so reliably typed
    if type(puzzleno) is int:
        urlsearch = urlpnum.format(puzzleno)
    elif type(puzzledate) is datetime.date:
        urlsearch = urlpnum.format(puzzleno)
    
    print("urlsearch = " + urlsearch)
    if urlsearch is None:
        raise Exception("ERROR in getpuzzleurl: No valid Search criteria")
    else:
        #searchhtml = None
        searchhtml = scrape.getpage(urlsearch, session)
    
    # Write to file while testing
    tmpfile = f"/home/harvey/Python/xword/tftt_search_{puzzleno}.html"
    """
    with open(tmpfile, 'w') as f:
        f.write(searchhtml)
    exit
    
    with open(tmpfile, 'r') as f:
        searchhtml = f.read()
    """
    
    if searchhtml is None:
        raise Exception("getpuzzleurl: Failed to get any Search results")
    
    # Find the href we want from the results
    # Search results return a list of <article>
    # The article <header> contains an anchor with the href in it
    # There are also footer links incl direct to Comments. Dont want that
    soup = bs4.BeautifulSoup(searchhtml, features="lxml")
    
    arts = soup.find_all('article')
    for art in arts:
        # Find a TfTT link anchor in this <article>. href itself may not contain the puzzleno
        aref = art.find('a', attrs={'href':re.compile('^https.*timesforthetimes')})
        if aref is None: continue
        print(aref.get_text())
        # Is it a link to this puzzle? puzzleno should be in the actual text
        if re.search(f'{puzzleno}', aref.get_text()) is not None:
            puzzleurl = str(aref.get('href'))
            break

    # Now we are up to date this could be because it has not been blogged yet
    if puzzleurl is None:
        with open(tmpfile, 'w') as f: f.write(searchhtml)
        raise Exception("getpuzzleurl: Failed to find regex puzzleno match")
        
    #print(puzzleurl)
    return puzzleurl
    
# End getpuzzleurl

# Get the clue tables out of the HTML and the clues from the tables
# Clues are accumulated in global clues[]
def getpuzzleclues(htmltxt):
    # Read clues from HTML
    # Clue section is in 2 tables: Across and Down. Comments are in another
    # These tables are unnamed and unclassed

    soup = bs4.BeautifulSoup(htmltxt, features="lxml")
    # Tables should be of class=clues but allow for inconsistency 
    tables = soup.find_all('table')

    # Across clues
    getclues(tables[0], "a")
    # Down clues
    getclues(tables[1], "d")
        
# End getpuzzleclues -----------------------------------------------------

#
# Get all of the clues from a HTML table
# Plus the solutions while we are at it
# Getting all this out in RegEx is too much hard work. Shame
# BeautifulSoup is built to parse html. Less elegant but easier
# TODO: Get the Solution too
# TODO: Can we get good enough info about type of clue? Anagram, CD etc.
#
def getclues(souptable, aord):
    # We want to jump about a bit in the souptable so parse with an iterator
    # No defined end point, let it raise StopIteration exception
    def nextrow():
        ret = True
        nonlocal souprow
        try:
            souprow = next(iterrows)
        except:
            ret = False
        return ret
    # End subfunction
            
    # Clues are in rows of 2 details: ClueNo and Clue text incl enumeration
    # <table> of class clues has 2 cols: num and clue
    # <td> should have classes: num, clue and ans. Not reliable
    # rx for finding numeric clueno
    rxcno = r'^\d{1,2}$'
    
    souprows = souptable.tbody.find_all('tr')
    rcnt = len(souprows)
    #print('<tr> count = ' + str(rcnt))
    if rcnt == 0: return
    
    souprow = souprows[0]
    iterrows = iter(souptable.tbody.find_all('tr'))
    
    while nextrow():
        #print(souprow.text)
        soupnum = souprow.find('td', attrs={'class': "num"})
        soupclue = souprow.find('td', attrs={'class': "clue"})
        # Non-standard template: try col[0] is numeric 
        if soupnum is None or soupclue is None:
            soupcols = souprow.find_all('td')
            coltxt = soupcols[0].text.strip()
            # Is this a numbered Clue row?
            if re.fullmatch(rxcno, coltxt) is not None:
                soupnum = soupcols[0]
                soupclue = soupcols[1]
        if soupnum is None or soupclue is None: continue
        # Create a Clue object using the avail cols
        oClue = createclue(aord, soupnum, soupclue)
        # Solution should be the next row
        if not nextrow(): break
        oClue.solntext = getsolution(souprow)
        print(oClue)
        oPuzzle.add_clue(oClue)
  
# End getclues ---------------------------------------------------------

# Separated out for readability
# The lack of begin/end code blocks is very disconcerting

def createclue(aord, soupno, soupclue):
    cno = soupno.text.strip()
    # Create the empty Clue object
    oClue = Clue(oPuzzle.pno, aord, cno)
    # Next col should be the clue text + (enumeration)
    ctxt = soupclue.text.strip()
    #print(ctxt)
    # Find enumeration. If this doesnt match something is wrong
    # Have to allow for spaces after (enum) + the occasional .
    rxenum = r'(\((?:[,-]*\d+)+\))[\W]*$'
    rxmatches = re.findall(rxenum, ctxt)
    # On absence of Enum: fail or try to calc later from soln? 
    if len(rxmatches) > 0:
        # Split Clue col into txt and enumeration
        cenum = rxmatches[0]
        oClue.cluetext = ctxt.replace(cenum,"").strip()
        oClue.enumeration = cenum
    else:
        #raise ValueError(f'Puzzle {pno}: No Enumeration found for {cno}{aord}')
        print(f'WARNING: {cno}{aord}: No Enumeration found')
        oClue.cluetext = ctxt.strip()
  
    oClue.defntext = getdefinition(soupclue)
    if oClue.defntext is None:
        print(f"WARNING: {cno}{aord} - No definition identified")
        oClue.defntext = oClue.cluetext
        
    return oClue

# End createclue -------------------------------------------------------------

def getdefinition(soupclue):
    ret = None  
    # Find the Definition part of the clue. Should be highlighted one way or another
    # Underlined, Red (thank you Dvynys), Bold (Dvynys again)
    # As a last resort, set defn = whole clue assuming it is a CD
    
    # Python stylists don't like this construct but it works as a COALESCE
    # Can't embed comments in it unfortunately 
    soupdefn = None or \
        soupclue.find('span', style=re.compile(r'underline')) or \
        soupclue.find('u') or \
        soupclue.find('span', style=re.compile(r'#ff0000')) or \
        soupclue.find(['b','strong']) or \
        soupclue.find('span', style=re.compile(r'bold')) or \
        soupclue

    if soupdefn is not None:
        ret = soupdefn.text.strip()
        
    return ret
    
# End getdefinition -------------------------------------------------------------

def getsolution(solnrow):
    ret = None
    # <td> should be of class ans. Try that 1st otherwise use the whole row
    # <table> of class clues has 2 cols: num and clue so in a soln row col[0] is empty 
    soupans = solnrow.find('td', attrs={'class': "ans"})
    if soupans is None:
        soupans = solnrow
   
    # Soln should be in the 1st Bold/Strong block
    soupsoln = soupans.find(['b','strong'])
    if soupsoln is None:
        soupsoln = soupans.find('span', style=re.compile(r'bold'))
        
    # TODO: If still blank get all the text up to "-"? Watch out for Unicode.
    if soupsoln is None: return
    #print(soupsoln)
    ret = soupsoln.text.strip()
    return ret
    
# End getsolution  -------------------------------------------------------------

# Get date and blogger from the post header
# Setter only appears in Sundays and only in the blog header text. Hmmm
def getpuzzlehdr(pno, htmltxt, puzzleurl):
    # Subfunction - Get the date
    # This turns out to be more PITA than it should be
    # Plus: For weekend puzzles blog date != puzzledate 
    def getdate(souphdr):
        # Found the date! It is actually held in an href to this URL
        # Find the href we want from the header and get the <time> tag
        dt = None
        # Find anchor points <a> where the href is to this pagename
        #print(puzzleurl)
        hrefs = souphdr.find_all('a', attrs={'href': puzzleurl})
        # Should only fail when testing on local copy
        if len(hrefs) == 0 :
            hrefs = soup.find_all('a', attrs={'href': re.compile(f'.*{pno}')})
        for link in hrefs:
            #print("Date link = " + link.text)
            # This is at least a proper time type albeit it in a silly format
            time = link.find('time', attrs={'class': re.compile(f'entry-date published')})
            if time is None: continue
            dtstr = time.attrs['datetime']    
            #dtparts = re.match(r'', dtstr)
            mat = re.match(r'^([0-9]{1,2})[a-z]{0,2}\s+([A-Za-z]{3,9})\s+([0-9]{4})', dtstr)
            dtstr = " ".join(mat.groups())
            dt = datetime.strptime(dtstr,'%d %B %Y')
            # If weekend we have 2 choices:
            # 1. Assume puzzle date is 7 days ago. Preferred
            # 2. Try and get it from blog header text. Not reliable.
            if dt.weekday() >= 5:
                wk1 = timedelta(days=7)
                dt = dt - wk1
            break # Got it
        # End of for loop hrefs
        return dt
    # End getdate subfunction ------------------------------------------------------------
    
    # getpuzzlehdr main body
    global oPuzzle
    dt = None
    auth = None
    # Convert text to soup
    soup = bs4.BeautifulSoup(htmltxt, features="lxml")
    # The whole header should be within a <header> type which also contains blogger
    for souphdr in soup.find_all('header', attrs={'class': re.compile(f'entry-header')}):
        dt = getdate(souphdr)
        if dt is None: continue
        # This is obviously the right header, now get the blogger which is also in an href
        oPuzzle.blogger = None
        soupauth = souphdr.find('a', attrs={'href': re.compile(f'author')})        
        auth = soupauth.get_text()
        break
    
    if dt is None:
        raise Exception("ERROR in getpuzzlehdr: No date found")
    if auth is None:
        raise Exception("ERROR in getpuzzlehdr: No author found")
    
    oPuzzle.pdate = dt
    oPuzzle.blogger = auth
    
    return

# End getpuzzlehdr ---------------------------------------------------------


###############################################################################
# MAIN
# Define a main to stop vars used here from being global

# for loop
# 	get_page
#	get_clues and solutions
#	save_clues with puzzle #, date etc. TODO: sqllite

def main():

    global oPuzzle
    
    # Foreach Puzzle by Cryptic puzzle #
    # Range does NOT include Stop value (Include Start, Exclude Stop)
    #for pno in range(29517,29518):

    ptype = "DX" # DX=Daily Cryptic, SX=Sunday Cryptic, QC, CN=Concise etc. Just in case
    # Test 29538 (non-standard), 29529 (standard)
    # Start: Monday 5 May 2025: 29221
    # Skipped due to blog generator failed, blogs typed in freehand!
    #	29331,29333,29355,29367
    # Update done after running. We could select max + 1 from DB
    done = 29589
    start = done + 1
    for pno in range(start,start + batchsize):
    #for pno in [29391]:
        print(f"Puzzle: {pno}")
        # Page URLs are not named simply https://tftt/number, we have to use the search
        url = getpuzzleurl(pno)
        if url is None: break
    
        # Tests. NOTE inconsistent URL naming
        #url = r'https://timesforthetimes.co.uk/times-cryptic-29538-sat-9-may-2026-nine-part-harmony'
        #url = r'https://timesforthetimes.co.uk/times-cryptic-no-29529'
        #localfile = f"/home/harvey/Python/xword/tftt_{pno}.html"
        #url = r'file://' + localfile
        print(url)
        
        # Sleep to mimic human activity. Mine certainly
        time.sleep(2)
    
        htmltxt = None
        if url.startswith("file"):
            with open(localfile, 'r') as f: htmltxt = f.read()
        else:
            htmltxt = scrape.getpage(url, session)
        
        # Get page fail. Better stop and see why before sending more requests
        if htmltxt is None: break
        
        # Write html to file while testing
        """
        with open(localfile, 'w') as f:
            f.write(htmltxt)
        """
        # Create a crossword.Puzzle object
        oPuzzle = Puzzle(pno, ptype)
        
        # Get date, blogger etc. from blog header
        getpuzzlehdr(pno, htmltxt, url)
        print(f'Date = {oPuzzle.pdate}, Blogger = {oPuzzle.blogger}')        
        
        # Get clue info from blog page
        getpuzzleclues(htmltxt)
        
        print('Clue Count = ' + str(len(oPuzzle.clues)))
        #for clue in oPuzzle.clues: print(clue)
        
        # Do we want the posts? Could extract my times? Ask starstrucka for it
        #posts = getposts(tables[2])
        
        if not oPuzzle.write_to_DB(conn):
            raise Exception("Database ERROR - do not continue")
        
        # Sleep to mimic human activity. Mine certainly
        time.sleep(3)
    # End puzzle loop
    
    # Tidy up
    conn.close()
    
# End of MAIN ---------------------------------------------------------------

# Run main with optional environment/context

batchsize = 3
now = datetime.now().strftime("%Y%m%d_%H%M%S")
log = f'wclog_{now}.txt'
# strftime("%I:%M%p on %B %d, %Y")

# We could append to this log if needed
# Need buffering set low so we can tail -f the logfile
if batchsize < 5:
    main()
else:
    with open(log, 'w', buffering=1) as f:
        with redirect_stdout(f):
            main()

# END PROGRAM
    

