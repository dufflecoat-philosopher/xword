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

# Get data into pandas dataframe. Same for any SQL

def get_dataframe(sql):
    
    with sqlite3.connect(dbpath) as conn:
        # Using a cursor
        #with conn.cursor() as cur:
            # Run the SQL to get a rowset
            #cur.execute(sql_wc)
            #rowset = cur.fetchall()
            #cur.close()
            
        # Run the SQL using pandas to get rowset into dataframe
        df = pd.read_sql_query(sql, conn)

    return df
# End of get_dataframe --------------------------------------------------------

# Avg WordCount by PuzzleNo

def get_wc_x_puzzle_data():
    # Could probably use simpler SQL and do more in pandas but old habits die hard
    # No point ordering because different charts need diff sequencing
    # Dont round too much, can do in pandas to suit graph
    # Alias to displayable names
    sql = '''\
SELECT p.pno as Puzzle, blogger as Blogger, setter as Setter,
    p.pdate, cast(strftime('%w',p.pdate) as INTEGER) as dno, p.dow as Day,
    max(s.nitch) as NITCH, 
	count(*) as Clues,
    round(avg(c.cluewc),4) as ClueWC,
    round(avg(c.defnwc),4) as DefnWC,
    round(avg(c.solnwc),4) as SolnWC,
    sum(case when c.defnwc = c.cluewc then 1 else 0 end) as CDs,
    sum(case when c.defnwc < c.cluewc and c.defnwc > 1 then 1 else 0 end) as DefnPhrases,
    sum(case when c.solnwc > 1 then 1 else 0 end) as SolnPhrases
from xwordpuzzles p, xwordclues c, snitch s
where c.pno = p.pno
and s.pno = p.pno
and p.pdate > date('now','-1 year')
group by p.pno
'''

    # Sorted in SQL but can re-order in pandas
    # Sort by x axis to make it like a time series. Do once across all before splitting.
    # Inplace means apply to self else assumes assignment to new df
    #df.sort_values(by=['pno','defnwc'], ascending=True, inplace=True)

    return get_dataframe(sql)
# End of get_wc_x_puzzle_data -------------------------------------------------


def get_witch_v_nitch_data():
    
    # Just get the data. Manipulate in pandas to split into traces etc    
    sql = '''\
-- Personal WITCH outer to include fails
SELECT
	p.pno as Puzzle, blogger as Blogger, setter as Setter,
    cast(strftime('%w',p.pdate) as INTEGER) as dno, p.dow as Day,
    max(w.pitch) as PITCH,
    max(w.witch) as WITCH, 
    max(s.nitch) as NITCH, 
    round(avg(c.cluewc),4) as ClueWC,
    round(avg(c.defnwc),4) as DefnWC,
    round(avg(c.solnwc),4) as SolnWC,
    sum(case when c.defnwc = c.cluewc then 1 else 0 end) as CDs,
    sum(case when c.defnwc < c.cluewc and c.defnwc > 1 then 1 else 0 end) as DefnPhrases,
    sum(case when c.solnwc > 1 then 1 else 0 end) as SolnPhrases
from xwordpuzzles p
join xwordclues c on c.pno = p.pno
join snitch s on s.pno = p.pno
left join pitch w on w.pno = p.pno
where 1=1
and p.pdate > date('now','-1 year')
group by p.pno
'''
    
    return get_dataframe(sql)
# End of get_witch_v_nitch_data -----------------------------------------------