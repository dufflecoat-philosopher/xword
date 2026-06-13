import sqlite3
# pandas - data structures for handling data in the code
import pandas as pd
# pathlib to find db file
from pathlib import Path

# Module Globals
# A module like this with no "main" can be treated like a static class in Python
dbpath = Path('assets/xword.db')
# List of available measures so all modules are in sync
wc_meas = ['ClueWC','DefnWC','SolnWC']

# Avg WordCount by PuzzleNo

def get_wc_x_puzzle_data():
    # Could probably use simpler SQL and do more in pandas but old habits die hard
    # No point ordering because different charts need diff sequencing
    # Alias to displayable names
    sql_wc = '''\
SELECT p.pno as Puzzle, blogger as Blogger, setter as Setter,
    cast(strftime('%w',p.pdate) as INTEGER) as dno, p.dow as Day,
    max(s.nitch) as Nitch, 
    round(avg(c.cluewc),2) as ClueWC,
    round(avg(c.defnwc),2) as DefnWC,
    round(avg(c.solnwc),2) as SolnWC,
    sum(case when c.defnwc = c.cluewc then 1 else 0 end) as CDs,
    sum(case when c.solnwc > 1 then 1 else 0 end) as Phrases
from xwordpuzzles p, xwordclues c, snitch s
where c.pno = p.pno
and s.pno = p.pno
group by p.pno
'''

    with sqlite3.connect(dbpath) as conn:
        # Using a cursor
        #with conn.cursor() as cur:
            # Run the SQL to get a rowset
            #cur.execute(sql_wc)
            #rowset = cur.fetchall()
            #cur.close()
            
        # Run the SQL using pandas to get rowset into dataframe
        df = pd.read_sql_query(sql_wc, conn)

    # Sorted in SQL but can re-order in pandas
    # Sort by x axis to make it like a time series. Do once across all before splitting.
    # Inplace means apply to self else assumes assignment to new df
    #df.sort_values(by=['pno','defnwc'], ascending=True, inplace=True)

    return df

# End of get_wc_x_puzzle_data -------------------------------------------------------------
