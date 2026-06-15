#
# Xword charts using plotly. Other charting tools are available
# 
# px vs go?
# go is lower level, px is built on top of go
# px has lots of ready made functionality but go is more flexible but more work to use
import plotly.express as px
#import plotly.graph_objects as go
import plotly.io as pio
from plotly import colors as pc

import numpy as np

import xworddata as xwd

# Constants

# SNITCH colours. These seem to be hand-picked rather than standard
colour_snitch_disc = ['#6dc17b','#b6d682','#ffeb89','#fdc580','#fa8e73','#d3d3d3','#778899']
# DoW colours. Similar idea to SNITCH but not the same so as not to confuse
colour_days = ['MediumSeaGreen','YellowGreen','Gold','Orange','OrangeRed','LightGrey','DarkGrey']

# This is hard work and the boundaries only approximate the precision of the real SNITCH
colour_snitch_cont = pc.make_colorscale([
    'rgb'+str(pc.hex_to_rgb("#6dc17b")),
    'rgb'+str(pc.hex_to_rgb("#6dc17b")),
    'rgb'+str(pc.hex_to_rgb("#b6d682")),
    'rgb'+str(pc.hex_to_rgb("#ffeb89")),
    'rgb'+str(pc.hex_to_rgb("#fdc580")),
    'rgb'+str(pc.hex_to_rgb("#fa8e73"))
],[
    0,0.095,0.238,0.309,0.452,1
]
)

# Globals
layout = {}

def layout_by_device(dev="desktop"):
    # Defaults are for desktop. Only change stuff for smaller formats
    layout['marker'] = dict(size=10, line=dict(width=1, color='Grey'))
    layout['showlegend']=True
    layout['showscale']=True
    
    match dev:
        case 'tablet':
            layout['marker'] = dict(size=8, line=dict(width=1, color='Grey'))
        case 'mobile':
            layout['marker'] = dict(size=5)
            layout['showlegend']=False
            layout['showscale']=False

# Run on import to init
layout_by_device(None)

# End of layout_by_device -----------------------------------------------------

def wc_x_puzzle(df, **kwargs):
    # Optional parameters
    dev = kwargs.get('device', None)
    layout_by_device(dev)
    
    #darkmode = kwargs.get('darkmode', None)
    pio.templates.default = 'plotly_white'
    
    figs = {}
    meas = xwd.wc_meas

    for m in meas:
        # Title measure
        tm = m.replace('WC','')
        # Basic plot
        fig = px.scatter(
            title=f"NITCH by Avg {tm} words ",
            data_frame=df, x=m, y='Nitch', color = 'Day', 
            custom_data=['Puzzle', 'Day', 'Blogger'],
            trendline='ols', trendline_scope='overall',
            trendline_color_override='DeepSkyBlue',
            color_discrete_sequence=colour_days
            )
        # Some of this formatting needs to be environment sensitive: Mobile vs Desktop
        fig.update_traces(
            hovertemplate='<br>'.join([
                '<b>Puzzle: %{customdata[0]}</b>',
                'Day: %{customdata[1]}',
                'Blogger: %{customdata[2]}',
                'WC: %{x}',
                'Nitch: %{y}',
            ]),
            marker=layout['marker'],
            selector=dict(mode='markers')
            )
        # Prevent the annoying zoom feature and allow drag scroll on mobile
        fig.update_layout(
            dragmode=False,
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),            
            margin=dict(t=50,b=20),
            title=dict(automargin=True),
            showlegend=layout['showlegend']
            )
        fig.update_coloraxes(showscale=layout['showscale'])
        
        figs[m] = fig
        # End of Measures loop
    
    return figs

# End of wc_x_puzzle ----------------------------------------------------------

# Scatters per day. Pretty but meaningless
def wc_x_dow(df, **kwargs):
    # Optional parameters
    dev = kwargs.get('device', None)
    layout_by_device(dev)
    
    pio.templates.default = 'plotly_white'
    
    figs = {}
    meas = xwd.wc_meas

    for m in meas:
        # Title measure
        tm = m.replace('WC','')
        # Basic plot
        fig = px.scatter(
            title=f"{tm} wordiness by Day",
            data_frame=df, x='Nitch', y=m, facet_col="Day", color='Nitch',
            custom_data=['Puzzle','Nitch','Blogger'],
            orientation='h',
            # plotly wont accept spacing = 0
            facet_col_spacing=0.001, facet_row_spacing=0.001,
            #color_discrete_sequence=colour_snitch
            color_continuous_scale=colour_snitch_cont
            )
        # Some of this formatting needs to be environment sensitive: Mobile vs Desktop
        fig.update_traces(
            hovertemplate='<br>'.join([
                '<b>Puzzle: %{customdata[0]}</b>',
                'Blogger: %{customdata[2]}',
                'WC: %{x}',
                'Nitch: %{customdata[1]}',
            ]),
            marker=layout['marker'],
            selector=dict(mode='markers')
            )
        # Prevent the annoying zoom feature and allow drag scroll on mobile
        fig.update_layout(
            dragmode=False,
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
            margin=dict(t=50,b=20),
            title=dict(automargin=True),
            showlegend=layout['showlegend']
            )
        """
        # Add a median marker line
        y_med = np.median(df[m])
        fig.add_shape(
            type="line",
            y0=y_med, x0=min(df['Nitch']),
            y1=y_med, x1=max(df['Nitch']),
            line=dict(color="Black", width=3, dash="dashdot"),
            )
        """
        figs[m] = fig
        # End of Measures loop
        
    return figs
    
# End of wc_x_dow -------------------------------------------------------------

# For testing charts without deployment env
def test():
    
    df = xwd.get_wc_x_puzzle_data()
    #figs = wc_x_puzzle(df)
    figs = wc_x_dow(df)
    for fig in figs.values(): fig.show(config={'displayModeBar': False})
    
# End of test

# Run this module alone to test
#test()