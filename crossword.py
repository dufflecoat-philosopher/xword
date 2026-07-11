#
# Crossword Classes
#
# Save data locally in sqlite
import sqlite3
# Regular expressions lib
import re
# Why does just import datetime not work?
from datetime import datetime

# Database interaction
# UPSERT is a PITA in sqlite. This ON CONFLICT mechanism is clunky but it works
sqlupsert_puzzle = '''INSERT INTO xwordpuzzles VALUES (\
:pno,:ptype,:pdate,:dow,:setter,:blogger\
)
ON CONFLICT (pno,ptype) DO
UPDATE set
pdate = :pdate,
dow = :dow,
setter = :setter,
blogger = :blogger
'''

sqlupsert_clues = '''INSERT INTO xwordclues VALUES (\
:pno,:ad,:clueno,\
:cluetext,:enumeration,:cluewc,\
:defntext,:defnwc,\
:solntext,:solnlen,:solnwc\
)
ON CONFLICT (pno,clueno,ad) DO
UPDATE set
cluetext = :cluetext,
enumeration = :enumeration,
cluewc = :cluewc,
defntext = :defntext,
defnwc = :defnwc,
solntext = :solntext,
solnlen = :solnlen,
solnwc = :solnwc
'''

# Python class names should be PascalCase
# https://pythonguides.com/python-naming-conventions/

class Puzzle(object):
    def __init__(self, pno, ptype, pdate=None):
        self.pno = pno
        self.ptype = ptype
        self.pdate = pdate
        self.setter = None
        self.blogger = None
        # 2 separate dictionaries to prevent duplicates        
        # Type annotation not avail until 3.5
        self._cluesa = {}
        self._cluesd = {}        
    
    # Make some attrs properties because when they get set we want to do other stuff        
    @property
    def pdate(self):
        return self._pdate
    @pdate.setter
    def pdate(self, value):
        self._pdate = value
        # dow can only be set when date is set
        if self._pdate is not None:
            self.dow = self._pdate.strftime("%a")
    
    # Make some attrs properties for more control
    # Return all Clues in a list
    @property
    def clues(self):
        lst = list(self._cluesa.values()) + list(self._cluesd.values())
        return lst
    
    # Public method to add/update clue
    def add_clue(self,clue):
        match clue.ad:
            case "a":
                self._cluesa[clue.clueno] = clue
            case "d":
                self._cluesd[clue.clueno] = clue
            case _:
                raise Exception("ERROR in crossword.Puzzle.add_clue: Invalid a or d")
        
        return # End of add_clue
    
        
    def write_to_DB(self,conn):
        ret = True
        try:
            # Puzzle first            
            # Everything needs a cursor in sqlite
            cur = conn.cursor()
            # Run the SQL 
            cur.execute(sqlupsert_puzzle, self.asdict())
            cur.close()
            
            # Clues
            cur = conn.cursor()
            # Insert can accept placeholder values as a tuple: row = (val1, val2, val3 ...)
            # sqlite.executemany is more efficient so create a list of rows
            upsertlist = []
            for clue in self.clues:
                upsertlist.append(clue.asdict())
            # Run the SQL 
            cur.executemany(sqlupsert_clues, upsertlist)
            cur.close()
            # All OK if we get here
            conn.commit()
        except Exception as e:
            print("ERROR in saveclues: " + str(e))
            conn.rollback()
            ret = False 
        finally:
            cur.close()

        return ret # End of write_to_DB
    
    def asdict(self):
        return {
            'pno': self.pno,
            'ptype': self.ptype,
            'pdate': self.pdate,
            'dow': self.dow,
            'setter': self.setter,
            'blogger': self.blogger
            }

# End of Puzzle ---------------------------------------------------

class Clue(object):
    # Init with minimum req for a clue to exist because the attrs can be added bit by bit
    def __init__(self, pno, aord, cno):
        self.pno = pno
        self.ad = aord
        self.clueno = cno
        self._cluetext = None
        self._enumeration = None
        self.cluewc = 0
        self._defntext = None
        self.defnwc = 0
        self._solntext = None
        self.solnlen = 0
        self.solnwc = 0
    
    def wc(self,txt):
        # re leaves empty strings where string ends in punctuation
        l = re.split(r'\W+', txt.strip())
        l = list(filter(None,l))
        return len(l)
        
    # Make some attrs properties because when they get set we want to do other stuff        
    @property
    def cluetext(self):
        return self._cluetext
    @cluetext.setter
    def cluetext(self, value):
        self._cluetext = value
        # Clue Word Count which is why I started this in the first place
        self.cluewc = self.wc(self._cluetext)
    
    @property
    def defntext(self):
        return self._defntext
    @defntext.setter
    def defntext(self, value):
        self._defntext = value
        self.defnwc = self.wc(self._defntext)
        
    @property
    def enumeration(self):
        return self._enumeration
    @enumeration.setter
    def enumeration(self, value):
        self._enumeration = value.replace("(","").replace(")","").strip()
        # Split returns list of strings. Map to numerics to sum
        enumstrlist = re.split(r',|-', self._enumeration)
        enumlist = list(map(int,enumstrlist))
        # Solution Word Count and total length. We should validate solntext vs this 
        self.solnwc = len(enumlist)
        self.solnlen = sum(enumlist)
    
    @property
    def solntext(self):
        return self._solntext
    @solntext.setter
    def solntext(self, value):
        self._solntext = value
        # If enum is missing calculate from soln
        if self._enumeration is None:
            e = ""
            ws = re.findall(r'(\w+)(\W+|$)', self._solntext)
            for w in ws:
                e += str(len(w[0])) + w[1].replace(" ",",")
            self.enumeration = e
    
    # String value of object for print()
    def __str__(self):
        ret = f'Clue: {self.clueno}{self.ad}: '+ self.cluetext + f' ({self.enumeration}), {self.defntext}, {self.solntext}'
        return ret
    
    # Bespoke dictionary because some things are properties. Was that wise?
    # This is better anyway, frees us up for syncing names 
    # These names should EXACTLY match the sqlite table so we can insert by Dictionary
    def asdict(self):
        return {
            'pno': self.pno,
            'ad': self.ad,
            'clueno': self.clueno,
            'cluetext': self.cluetext,
            'enumeration': self.enumeration,
            'cluewc': self.cluewc,
            'defntext': self.defntext,
            'defnwc': self.defnwc,
            'solntext': self.solntext,
            'solnlen': self.solnlen,
            'solnwc': self.solnwc
            }
    
# End of Clue ---------------------------------------------------
