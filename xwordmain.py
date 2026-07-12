#
# App main
# Set up env before importing funcs that will use it 
# 
import streamlit as st
# Detects user device type
from streamlit_user_device import user_device

# mobile/tablet/laptop
device = user_device()
#dev = "mobile"
#if dev: st.write(dev)
    
# Can force theme to light in config.toml or just pick mid-range colours
#theme = st_theme()
#st.write(theme)

import xwordslit

xwordslit.main(device)


