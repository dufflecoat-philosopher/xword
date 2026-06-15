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

# mobile/tablet/laptop
dev = user_device()
#dev = "mobile"
#if dev: st.write(dev)

# Can force theme to light in config.toml or just pick mid-range colours
#theme = st_theme()
#st.write(theme)

# Get the charts
df = xwd.get_wc_x_puzzle_data()
figs1 = xwc.wc_x_puzzle(df, device=dev)
figs2 = xwc.wc_x_dow(df, device=dev)

# Battling the layout:
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

# Mostly using the container to show border of this vs streamlit wrapper
# gap=Small/Medium/Large/None

with st.container(gap=None, vertical_alignment='top', horizontal_alignment='left'):
    # Can probably use st.subheader or something
    # Used html while testing the bits we have minimised to save space 
    st.html('<b style="font-size:200%;">Times Cryptic Wordiness</b>')
    
    # Tabs for mobile, columns for desktop?
    # Manual tab naming for now
    tabs = st.tabs(['Clue','Definition','Solution'], key='myTabsWCNitch')
    for i in range(0,len(tabs)):
        m = meas[i]
        with tabs[i]:
            with st.container(gap=None, border=True):
                st.plotly_chart(figs1[m], config=chart_config, key=f'{m}1')         
            with st.container(gap=None, border=True):
                st.plotly_chart(figs2[m], config=chart_config, key=f'{m}2')
            

