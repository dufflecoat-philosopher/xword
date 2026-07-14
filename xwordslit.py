#
# Streamlit deployment
# 
import streamlit as st
# Detects user device type
from streamlit_user_device import user_device
#dev = user_device()
#print(f"device={dev}")

# pathlib to find css files
from pathlib import Path
from datetime import datetime

import xworddata as xwd
import xwordplotly as xwc
import xwordtxt as txt

# Globals

# Controls for interactive charting: Zoom etc. Probably OK in desktop mode
chart_config = {'displayModeBar': False}

# Caching - worth setting timeout?
# There are a small fixed # of cachable things here

# Get data from DB. Its tiny, this is quick but might as well play with caching
# Run sequentially, its tiny and sqlite is single user

@st.cache_data
def get_counts_data():
    return xwd.get_wc_x_puzzle_data()

@st.cache_data
def get_witch_data():
    return xwd.get_witch_v_nitch_data()

# Save as globals rather than passing all over the place
dfc = get_counts_data()
dfw = get_witch_data()

# Charts
# Note: Charts were all written to do a list of meas so return a dict of figs
# We want to cache the plotly figs then run the tabs as parallel fragments 

@st.cache_resource
def get_count_plot(m, dev):
    figs = xwc.wc_x_puzzle(dfc, meas=[m], device=dev)
    return figs[m]
    
@st.cache_resource
def get_dow_plot(m, dev):
    figs = xwc.wc_x_dow(dfc, meas=[m], device=dev)
    return figs[m]

@st.cache_resource
def get_witch_plot(m, dev):
    figs = xwc.wc_witch_v_nitch(dfw, meas=[m], device=dev)
    return figs[m]

# Keeping things tidier
def sl_commentry(txt):
    with st.expander('Commentry'):
        st.write(txt)
    
def sl_plotly(fig, uniqkey):
    with st.container(gap=None, border=True):
        st.plotly_chart(fig, config=chart_config, key=uniqkey)

# FRAGMENTS
# I think the plotly bit is quick and the slowness is down to web rendering (as always)
# Splitting into parallel fragments should, in theory be quicker
# Could do each chart as a fragment but if 2 charts on 1 tab we want to control which displays first
# Therefore 1 fragment per Tab

@st.fragment(parallel=True)
def sl_all_clue(dev):
    m = 'ClueWC'
    # WC
    fig = get_count_plot(m, dev)
    sl_plotly(fig, f'All{m}')
    # DOW  
    fig = get_dow_plot(m, dev)
    sl_plotly(fig, f'AllDow{m}')
    
@st.fragment(parallel=True)
def sl_all_defn(dev):
    m = 'DefnPhrases'
    fig = get_count_plot(m, dev)
    sl_plotly(fig, f'All{m}')
    m = 'CDs'
    fig = get_count_plot(m, dev)
    sl_plotly(fig, f'All{m}')
    
@st.fragment(parallel=True)
def sl_all_soln(dev):
    m = 'SolnPhrases'
    fig = get_count_plot(m, dev)
    sl_plotly(fig, f'All{m}')

@st.fragment(parallel=True)
def sl_user_clue(dev):
    m = 'ClueWC'
    fig = get_witch_plot(m, dev)
    sl_plotly(fig, f'User{m}')
    
@st.fragment(parallel=True)
def sl_user_defn(dev):
    m = 'DefnPhrases'
    fig = get_witch_plot(m, dev)
    sl_plotly(fig, f'User{m}')
    
@st.fragment(parallel=True)
def sl_user_soln(dev):
    m = 'SolnPhrases'
    fig = get_witch_plot(m, dev)
    sl_plotly(fig, f'User{m}')

#
# Runtime NOTEs:
#	The first time this runs will be server-only so no session-state
#	We can set a device default anyway because any caching will still be worth it
#	Probably no point in using session_state here but useful learning

def main():
    # Session state is really a dictionary but supports this attribute syntax
    dev = user_device() # = None in initial streamlit server-only run
    #print(f"user_device() says {dev}")
    st.session_state.device = dev or 'desktop' # mobile/tablet/laptop
        
    # Get latest date
    strdate = dfc['pdate'].max()
    maxdate = datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S").date()
    strdate = maxdate.strftime("%a, %d %b %Y") 
    #print(strdate)

    # Battling the Streamlit layout:
    # https://medium.com/codetodeploy/getting-the-most-out-of-your-streamlit-page-maximizing-the-screen-use-13c2b8c5a87d

    # Default layout centres and only uses half the screen
    st.set_page_config(layout="wide")

    # Space at the top:
    # Header class=stAppHeader
    #	Div class=stAppToolBar
    # Section class=stMain
    #	Div class=stMainBlockContainer - This is us
    #		Div class=stVerticalBlock - blank space with height=Auto
    #			Div class=stElementContainer - blank part of parent
    #			Div class=stLayoutWrapper - now we're getting closer to our stuff
    #				Div class=stVerticalBlock - This is my stContainer

    st.html(Path('assets/streamlit.css'))
    st.html(Path('assets/xword_streamlit.css'))

    # Start the actual layout
    # Mostly using the outer container to show border of this vs streamlit wrapper
    # Border removed after testing
    # gap=Small/Medium/Large/None

    with st.container(gap=None, vertical_alignment='top', horizontal_alignment='left'):
        
        # mobile/tablet/laptop
        dev = st.session_state.device
        
        with st.container(horizontal=True):
            # Used html while testing the bits we have minimised to save space
            #st.html('<b style="font-size:200%;">Times Cryptic Wordiness</b>')
            st.subheader("Times Cryptic Wordiness", width='content')
            #with st.popover("", icon=':material/info:', help='Info'):
            #    st.write(f"Device type = {dev}" )
        
        # Tabs for mobile, columns for desktop?
        # Manual tab naming for now
        # Show global trend first, its of more general interest
        tabSpiel, tabAll, tabUser = st.tabs(['Intro','Everyone','rv1'], key='myTabsTop')

        # TODO:
        with tabSpiel:
            with st.expander('Premise'):
                st.write(txt.txt_background)
                st.write(f"All data covers 12 months to {strdate}.")
            with st.expander('Conclusion'):
                st.write(txt.txt_conclusion)
            with st.expander('Credits'):
                st.write(txt.txt_thanks)   
            with st.expander('Tech bits'):
                st.write(txt.txt_tech)    
                st.write(f"Currently running in {dev} mode")     
            
        with tabAll:
            tabAllClue, tabAllDefn, tabAllSoln = st.tabs(['Clue','Definition','Solution'], key='myTabsNitch')
            with tabAllClue:
                sl_commentry(txt.txt_clue)
                sl_all_clue(dev)
            with tabAllDefn:
                sl_commentry(txt.txt_defn)
                # Phrase count + CDs just for completeness
                sl_all_defn(dev)
            with tabAllSoln:
                sl_commentry(txt.txt_soln)
                # Phrase Count is deffo the more meaningful here
                sl_all_soln(dev)
                    
        with tabUser:
            tabUserClue, tabUserDefn, tabUserSoln = st.tabs(['Clue','Definition','Solution'], key='myTabsSolver')
            with tabUserClue:
                sl_commentry(txt.txt_solver_clue)
                sl_user_clue(dev)
            with tabUserDefn:
                sl_commentry(txt.txt_solver_defn)
                sl_user_defn(dev)
            with tabUserSoln:
                sl_commentry(txt.txt_solver_soln)
                sl_user_soln(dev)
                
# End main

# TEST
#main()

            

