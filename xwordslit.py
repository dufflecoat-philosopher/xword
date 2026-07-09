#
# Streamlit deployment
# 
import streamlit as st
# Detects user device type
from streamlit_user_device import user_device
# Dictionary including base = light/dark/system/custom
# import st-theme

# pathlib to find css files
from pathlib import Path

import xworddata as xwd
import xwordplotly as xwc
import xwordtxt as txt

# mobile/tablet/laptop
dev = user_device()
#dev = "mobile"
#if dev: st.write(dev)
    
# Can force theme to light in config.toml or just pick mid-range colours
#theme = st_theme()
#st.write(theme)

# Get WC data. Its tiny, this is quick
df = xwd.get_wc_x_puzzle_data()
dfw = xwd.get_witch_v_nitch_data()

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

# Controls for interactive charting: Zoom etc. Probably OK in desktop mode
chart_config = {'displayModeBar': False}

# We want to loop through Measures
meas = xwd.wc_meas

# And the charts
# Note: Charts were all written to do a list of meas so return a dict of figs

# Keeping things tidier
def sl_commentry(txt):
    with st.expander('Commentry'):
        st.write(txt)
    
def sl_plotly(fig, uniqkey):
    with st.container(gap=None, border=True):
        st.plotly_chart(fig, config=chart_config, key=uniqkey)
        
# I think the plotly bit is quick and the slowness is down to web rendering (as always)
# Do each chart as fragments anyway, might as well

@st.fragment(parallel=True)
def sl_all_clue_wc():
    m = 'ClueWC'
    figs = xwc.wc_x_puzzle(df, meas=[m], device=dev)
    sl_plotly(figs[m], f'All{m}')
@st.fragment(parallel=True)
def sl_all_clue_dow():
    m = 'ClueWC'
    figs = xwc.wc_x_dow(df, meas=[m], device=dev)
    sl_plotly(figs[m], f'AllDow{m}')
@st.fragment(parallel=True)
def sl_all_defn_ph():
    m = 'DefnPhrases'
    figs = xwc.wc_x_puzzle(df, meas=[m], device=dev)
    sl_plotly(figs[m], f'All{m}')
@st.fragment(parallel=True)
def sl_all_defn_cd():
    m = 'CDs'
    figs = xwc.wc_x_puzzle(df, meas=[m], device=dev)
    sl_plotly(figs[m], f'All{m}')
@st.fragment(parallel=True)
def sl_all_soln_ph():
    m = 'SolnPhrases'
    figs = xwc.wc_x_puzzle(df, meas=[m], device=dev)
    sl_plotly(figs[m], f'All{m}')

@st.fragment(parallel=True)
def sl_user_clue_wc():
    m = 'ClueWC'
    figs = xwc.wc_witch_v_nitch(dfw, meas=[m], device=dev)
    sl_plotly(figs[m], f'User{m}')
@st.fragment(parallel=True)
def sl_user_defn_ph():
    m = 'DefnPhrases'
    figs = xwc.wc_witch_v_nitch(dfw, meas=[m], device=dev)
    sl_plotly(figs[m], f'User{m}')
@st.fragment(parallel=True)
def sl_user_soln_ph():
    m = 'SolnPhrases'
    figs = xwc.wc_witch_v_nitch(dfw, meas=[m], device=dev)
    sl_plotly(figs[m], f'User{m}')
    
# Mostly using the outer container to show border of this vs streamlit wrapper
# Border removed after testing
# gap=Small/Medium/Large/None

with st.container(gap=None, vertical_alignment='top', horizontal_alignment='left'):
    
    with st.container(horizontal=True):
        # Used html while testing the bits we have minimised to save space
        #st.html('<b style="font-size:200%;">Times Cryptic Wordiness</b>')
        st.subheader("Times Cryptic Wordiness", width='content')
        #with st.popover("", icon=':material/info:', help='Background Info'):
        #    st.write(txt.txt_background)
    
    # Tabs for mobile, columns for desktop?
    # Manual tab naming for now
    # Show global trend first, its of more general interest
    tabSpiel, tabAll, tabUser = st.tabs(['Intro','Everyone','Solver'], key='myTabsTop')

    # TODO:
    with tabSpiel:
        with st.expander('Premise'):
            st.write(txt.txt_background)
        with st.expander('Conclusion'):
            st.write(txt.txt_conclusion)
        with st.expander('Thanks'):
            st.write(txt.txt_thanks)        
        
    with tabAll:
        tabAllClue, tabAllDefn, tabAllSoln = st.tabs(['Clue','Definition','Solution'], key='myTabsNitch')
        with tabAllClue:
            # ClueWC + DoW
            sl_all_clue_wc()
            sl_all_clue_dow()
        with tabAllDefn:
            sl_commentry(txt.txt_defn)
            # Phrase count + CDs just for completeness
            sl_all_defn_ph()
            sl_all_defn_cd()
        with tabAllSoln:
            sl_commentry(txt.txt_soln)
            # Phrase Count is deffo the more meaningful here
            sl_all_soln_ph()
                
    with tabUser:
        tabUserClue, tabUserDefn, tabUserSoln = st.tabs(['Clue','Definition','Solution'], key='myTabsSolver')
        with tabUserClue:
            sl_commentry(txt.txt_solver_clue)
            sl_user_clue_wc()
        with tabUserDefn:
            sl_commentry(txt.txt_solver_defn)
            sl_user_defn_ph()
        with tabUserSoln:
            sl_commentry(txt.txt_solver_soln)
            sl_user_soln_ph()
            
# The end

            

