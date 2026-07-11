#!/home/harvey/Python/venvs/rv python

# Web scrape from SNITCH
# Much simpler affair than TfTT

# Why does just import datetime not work?
from datetime import datetime, timedelta
# Regular expressions lib
# https'://docs.python.org/3/library/re.html
#import re
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
# My http scraping lib
import scrape

# Constants
dbpath = Path('assets/xword.db')
# Main page is for Times Cryptic
urlsnitch = "https://times.xwdsnitch.link/"
# There are separate pages for QC and any others
urlcryptic = urlsnitch


# Globals
# DX=Daily Cryptic, SX=Sunday Cryptic, QC, CN=Concise etc. Just in case
ptype = None
# HTTP session
session = requests.session()
# No need to keep reopening DB connection 
conn = sqlite3.connect(dbpath)
# List of Nitch objects for DB entry
scores = []

# A NITCH entry is similar to a puzzle but without all the Clue data
# Dont need a special AsDict func, so simple the built-in __dict__ will do
# Scraped Solver data is identical but we just add solver in
# Solver is done in 2 parses: 1 for NITCH, 1 for WITCH 
# Separate table because solver could in theory get quite big with lots of solvers
#	but share the same class to enable code sharing
class Nitch(object):
    def __init__(self, pno, ptype, pdate, nitch):
        self.pno = pno
        self.ptype = ptype
        self.pdate = pdate
        self.dow = self.pdate.strftime("%a")
        # Keep Sunday separate
        if self.ptype == 'DX' and self.dow == "Sun":
            self.ptype = 'SX'
        self.nitch = nitch
        
        # These will be unused by the main SNITCH SQL
        self.solver = "ALL"
    
    def __str__(self):
        ret = f'{self.solver},{self.pno},{self.ptype},{self.pdate},{self.dow},{self.nitch}'
        return ret
# END of Nitch

# Database interaction
# UPSERT is a PITA in sqlite. This ON CONFLICT mechanism is clunky but it works
sqlupsert_snitch = '''INSERT INTO snitch VALUES (\
:pno,:ptype,:pdate,:dow,:nitch\
)
ON CONFLICT (pno,ptype) DO
UPDATE set
pdate = :pdate,
dow = :dow,
nitch = :nitch
'''
# PITCH = personal NITCH
sqlupsert_pitch = '''INSERT INTO pitch VALUES (\
:solver,:pno,:ptype,:pdate,:dow,:nitch,0\
)
ON CONFLICT (pno,ptype,solver) DO
UPDATE set
pdate = :pdate,
dow = :dow,
pitch = :nitch
'''
# WITCH = wavelength NITCH
sqlupsert_witch = '''INSERT INTO pitch VALUES (\
:solver,:pno,:ptype,:pdate,:dow,0,:nitch\
)
ON CONFLICT (pno,ptype,solver) DO
UPDATE set
pdate = :pdate,
dow = :dow,
witch = :nitch
'''

def write_to_DB(conn,sql):
    ret = True
    try:          
        # Everything needs a cursor in sqlite
        cur = conn.cursor()
        # Insert can accept placeholder values as a tuple: row = (val1, val2, val3 ...)
        # sqlite.executemany is more efficient so create a list of rows
        upsertlist = []
        for nitch in scores:
            upsertlist.append(nitch.__dict__)
        # Run the SQL
        cur.executemany(sql, upsertlist)
        cur.close()
        # All OK if we get here
        conn.commit()
    except Exception as e:
        print("ERROR in write_to_DB: " + str(e))
        conn.rollback()
        ret = False 
    finally:
        cur.close()

    return ret # End of write_to_DB

# Parse NITCH table adding to global scores list
def get_nitch_table(souptable, solver):
    
    global scores
    scores = []
    d1 = timedelta(days=1)
    
    # Each Row starts with a weekly avg + wc date
    # Rest of Columns need to be treated in pairs: PuzzleNo + NITCH
    for row in souptable.find_all('tr'):
        #print(row.get_text())
        cols = row.find_all('td')
        if len(cols) == 0: continue
        # Ignore avg in col[0]
        wc = cols[1].get_text(strip=True)        
        if wc == "": continue
        # At least date is in a sensible format here
        pdate = datetime.strptime(wc,'%Y-%m-%d')
        for i in range(2, len(cols)):
            txt = cols[i].get_text(strip=True)
            if txt == "": continue
            p = i % 2
            match p:
                case 0:
                    pno = int(txt)
                case 1:
                    score = int(txt)
                    oNitch = Nitch(pno, ptype, pdate, score)
                    oNitch.solver = solver
                    scores.append(oNitch)
                    # Move date on for the next day. 1st day is wc date
                    pdate = pdate + d1
            # End of Match
        # End of cols loop
                    
# Can potentially use this in a loop to get all solvers
def get_solver_url(solver):
    # Hardcoded to rv1 for now
    url = 'https://times.xwdsnitch.link/solvers/3872'
    print(f'solver_url = {url}')
    return url
    
# Get 1 month NITCH and WITCH tables
# These tables follow same pattern as home page (minus the w/e days) so can share code
def get_solver(solver):
    
    url = get_solver_url(solver)
    htmltxt = scrape.getpage(url, session)
    
    # No content-specific html object classes here
    # Several tables: 1: Top 10, 2: NITCH, 3: WITCH
    # Nothing to distinguish the 2 we want so:
    # 	a) Use preceding header. Tricky
    #	b) Use order of occurrence. Easier
    soup = bs4.BeautifulSoup(htmltxt, features="lxml")
    souptables = soup.find_all('table')
    
    seq = 1
    for table in souptables:
        th = table.find('th', string="Week beginning")
        if th is None: continue
        # We've found the right kind of table 
        get_nitch_table(table, solver)
        for nitch in scores: print(nitch)
        # NITCH or WITCH
        match seq:
            case 1: # NITCH (PITCH)
                write_to_DB(conn, sqlupsert_pitch)
                seq += 1
            case 2: # WITCH
                write_to_DB(conn, sqlupsert_witch)
                break

# End of get_solver -----------------------------------------------------------

def get1year(url):

    htmltxt = scrape.getpage(url, session)
    
    # No content-specific html object classes here
    # Several tables: 1 per recent few days then 1 big one for past year
    # Get the past years worth
    tabyr = None
    soup = bs4.BeautifulSoup(htmltxt, features="lxml")
    souptables = soup.find_all('table')
    for table in souptables:
        th = table.find('th', string="Week beginning")
        if th is None: continue
        tabyr = table
        break

    if tabyr is None: return
    
    # Parse into global scores list
    get_nitch_table(tabyr, None)
    
    for nitch in scores: print(nitch)
    write_to_DB(conn, sqlupsert_snitch)

# End of get1year -------------------------------------------------------------

def main():

    global ptype
    ptype = "DX"
    match ptype:
        case "DX": url = urlcryptic
        case _ : url = urlsnitch
        
    # Main NITCH page
    get1year(url)
    
    # Solver WITCH
    get_solver("rv1")
    
    conn.close()
    
# END main

main()
