#
# App main
# Set up env before importing funcs that will use it 
#
import xwordenv as env

# Detects user device type
from streamlit_user_device import user_device
# mobile/tablet/laptop
device = user_device()
#dev = "mobile"
#if dev: st.write(dev)
env.device = device

# Environment vars initiated

# Import and Start the Streamlit app
import xwordslit

xwordslit.main()


