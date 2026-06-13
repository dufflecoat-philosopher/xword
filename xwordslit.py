#
# Streamlit deployment
# 
import streamlit as st
# Detects user device type
from streamlit_user_device import user_device

# pathlib to find css files
from pathlib import Path

import xworddata as xwd
import xwordplotly as xwc

dev = user_device()
#if dev: st.write(dev)
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

chart_config = {'displayModeBar': False}

# We want to loop through Measures
meas = xwd.wc_meas

# Mostly using the container to show border of this vs streamlit wrapper

with st.container(border=True, vertical_alignment='top', horizontal_alignment='left'):
    
    # DONT use st.header because Streamlit puts it OUTSIDE of this container
    #	in with the bits we have minimised to save space 
    st.html('<b style="font-size:200%;">Times Cryptic Wordiness</b>')

    with st.container():
        #tabs = st.tabs([d['title'] for d in tablist])
        tabs = st.tabs(meas, key='xwordmeas')
        for i in range(0,len(tabs)):
            m = meas[i]
            with tabs[i]:
                st.plotly_chart(figs1[m], config=chart_config, key=f'{m}1')
                st.plotly_chart(figs2[m], config=chart_config, key=f'{m}2')

