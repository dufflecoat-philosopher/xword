import streamlit as st
import sqlite3
# pandas - data structures for handling data in the code
import pandas as pd
# px vs go?
# go is lower level, px is built on top of go
# px has lots of ready made functionality but go is more flexible but more work to use
import plotly.express as px
import plotly.graph_objects as go
#import plotly.graph_objects as go

#fig = px.bar(x=['a', 'b', 'c'], y=[1, 3, 2])
#fig.show()

sql_wc = '''\
SELECT p.pno as Puzzle, blogger as Blogger,
    cast(strftime('%w',p.pdate) as INTEGER) as dno, p.dow as Day,
    max(s.nitch) as Nitch, 
	round(avg(c.cluewc),2) as ClueWC,
	round(avg(c.defnwc),2) as DefnWC,
	round(avg(c.solnwc),2) as SolnWC
from xwordpuzzles p, xwordclues c, snitch s
where c.pno = p.pno
and s.pno = p.pno
group by p.pno
order by dno, defnwc
'''

# No need to keep reopening DB connection 
with sqlite3.connect('xword.db') as conn:
    #with conn.cursor() as cur:
        # Run the SQL to get a rowset
        #cur.execute(sql_wc)
        #rowset = cur.fetchall()
        #cur.close()
    # Run the SQL using pandas to get a dataframe (like a rowset)
    rs = pd.read_sql_query(sql_wc, conn)
    #print(rs)
    #conn.rollback()
    #conn.close()

# Pandas DF slicing into days
dow = {}
pxfigs = {}
alldata = ()
# Its impossible to access Streamlit elements programmatically! Don't like it
# Set up the structure in proper Python for iterating
tablist = [
    {'title': 'Clue', 'meas': 'ClueWC'},
    {'title': 'Definition', 'meas' :'DefnWC'},
    {'title': 'Solution', 'meas' :'SolnWC'}
    ]
# Sorted in SQL but can re-order in pandas
# Sort by x axis to make it like a time series. Do once across all before splitting.
# Inplace means apply to self else assumes assignment to new df
#rs.sort_values(by=['pno','defnwc'], ascending=True, inplace=True)
# Ignore Sun
df = rs.loc[rs['dno'] < 6]

# Repeat the same thing for each measure? Or make it interactive?
for tab in tablist:
    m = tab['meas']
    t = m.replace('WC', ' Word Count')
    # Splitting by color automatically adds a trendline EACH. Hurrah!
    pxfigs[m] = px.scatter(rs, x=m, y='Nitch', trendline='ols', color = 'Day', title = t,
                            color_discrete_sequence=px.colors.qualitative.Plotly,
                            custom_data=['Puzzle', 'Day', 'Blogger'])
    #facet_col='dow', color='dow',

    pxfigs[m].update_traces(
        hovertemplate='<br>'.join([
            '<b>Puzzle: %{customdata[0]}</b>',
            'Day: %{customdata[1]}',
            'Blogger: %{customdata[2]}',
            '%{m}: %{x}',
            'Nitch: %{y}',
        ]),
        marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')),
        selector=dict(mode='markers')
        )
    
#for fig in pxfigs.values(): fig.show()
    
# Separate layout from all the above stuff?

st.title('Times Cryptic Wordiness')
#c = st.container()
tabs = st.tabs([d['title'] for d in tablist])
for i in range(0,len(tablist)):
    m = tablist[i]['meas']
    with tabs[i]:
        st.plotly_chart(pxfigs[m])
