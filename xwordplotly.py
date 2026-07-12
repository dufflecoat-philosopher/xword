#
# Xword charts using plotly. Other charting tools are available
# NOTE: These funcs could be run multi-threaded so:
#	No Globals
#	No updating objects passed in. Make a copy
#	If still problems create a Class so multiple instances can be created
# 
# px vs go?
# go is lower level, px is built on top of go
# px has lots of ready made functionality but go is more flexible but more work to use
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly import colors as pc

import pandas as pd
import numpy as np
import re

import xworddata as xwd

# Constants

pio.templates.default = 'plotly_white'

# SNITCH colours. These seem to be hand-picked rather than html colours
colour_snitch = ['#6dc17b','#b6d682','#ffeb89','#fdc580','#fa8e73']
# Greys for the weekend
colour_snitch_we = ['#d3d3d3','#778899']
# DoW colours. Similar idea to SNITCH but not the same. Confusing?
#colour_days = ['MediumSeaGreen','YellowGreen','Gold','Orange','OrangeRed','LightGrey','DarkGrey']
# DoW using continuous scale converted to discrete for Mon-Fri
colour_days = pc.sample_colorscale('Tealgrn', np.linspace(0,1,5))
# Add grey for Saturday
colour_days.append('rgb'+str(pc.hex_to_rgb(colour_snitch_we[0])))
#print(colour_days)

# NITCH discrete converted to continuous
# Neat but hard work and the boundaries only approximate the precision of the real SNITCH
# Ranges start from 0 so there is an extra entry for 0
rgbs = ['rgb'+str(pc.hex_to_rgb(colour_snitch[0]))]
for i in range(len(colour_snitch)):
    rgbs.append('rgb'+str(pc.hex_to_rgb(colour_snitch[i])))
colour_snitch_cont = pc.make_colorscale(rgbs,[0,0.095,0.238,0.309,0.452,1])

# Common settings for all this set of charts

def xword_layout(fig):
        
    # Prevent the annoying zoom feature and allow drag scroll on mobile
    # The drag feature is impressive when rotating 3D charts, not needed here.
    # Reduce top/bottom margin padding
    fig.update_layout(
        dragmode=False,
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True),            
        margin=dict(t=50,b=20),
        title=dict(automargin=True)
        )
    
# End of xword_layout

# Hover construction is quite repetitive - share code
# Accept list of tuples because dict may not be ordered
# The 1st item is the header

def xword_hover(data = []):
    
    #print(data)
    hover = None
    if len(data) == 0: return hover
    
    items = []
    for i in range(len(data)):
        k,v = data[i]
        txt = ""
        if k is not None:
            txt = f"{k}: "
            
        if type(v) == int:
            txt += f"%{{customdata[{v}]}}"
        else:
            txt += f"%{{{v}}}"

        if i == 0:
            txt = f"<b>{txt}</b>"
            
        items.append(txt)
    # End for loop
     
    hover = '<br>'.join(items)
    #print(hover)
    return hover
# End of xword_hover ----------------------------------------------------------

def wc_x_puzzle(df_in, meas=xwd.wc_meas, **kwargs):
    # Optional parameters
    dev = kwargs.get('device', None)
    
    # layout_by_device. Too bespoke to each chart 
    # Defaults are for desktop. Only change stuff for smaller formats
    marker = dict(size=10, line=dict(width=1, color='Grey'))
    legend = dict(orientation='v',itemsizing='constant')
    
    match dev:
        case 'tablet':
            marker = dict(size=8, line=dict(width=1, color='Grey'))
        case 'mobile':
            marker = dict(size=4)
            # anchor top/bottom refers to the t/b of the legend, not the plot
            legend = dict(orientation='h', itemsizing='constant',
                          yanchor='top', y=-0.2, xanchor='left'
                          )
    
    # Need it sorted by Day number for the colour scale
    df = df_in.sort_values(['dno']) #, inplace=True)
    
    figs = {}

    for m in meas:
        # Title measure
        tm = m.replace('WC','Words')
        tm = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', tm)
        # Basic plot
        fig = px.scatter(
            title=f"NITCH by Avg {tm}",
            data_frame=df, x=m, y='NITCH', color = 'Day', 
            custom_data=['Puzzle', 'Day', 'Blogger'],
            trendline='ols', trendline_scope='overall',
            trendline_color_override='DeepSkyBlue',
            color_discrete_sequence=colour_days
            )
        # Some of this formatting needs to be environment sensitive: Mobile vs Desktop
        # Can we make it common? Call it from the front end layer?
        fig.update_traces(
            hovertemplate = xword_hover([('Puzzle',0),('Day',1),('Blogger',2),('Count','x'),('NITCH','y')]),
            marker=marker,
            selector=dict(mode='markers')
            )
        fig.update_layout(
            legend=legend
            )
        # Shared layout settings for all these charts
        xword_layout(fig)
        
        figs[m] = fig
        # End of Measures loop
    
    return figs

# End of wc_x_puzzle ----------------------------------------------------------

# Scatters per day. Pretty but meaningless
def wc_x_dow(df_in, meas=xwd.wc_meas, **kwargs):
    # Optional parameters
    dev = kwargs.get('device', None)

    # layout_by_device. Too bespoke to each chart to share
    # Default = desktop
    marker = dict(size=10, line=dict(width=1, color='Grey'))
    showscale=True
    match dev:
        case 'tablet':
            # Tablet is not so different to desktop
            marker = dict(size=8, line=dict(width=1, color='Grey'))
        case 'mobile':
            marker = dict(size=5)
            showscale=False

    # Need it sorted by Day number for facets
    df = df_in.sort_values(['dno']) #, inplace=True)

    figs = {}
    
    for m in meas:
        # Title measure
        tm = m.replace('WC','')
        tm = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', tm)
        # Basic plot
        fig = px.scatter(
            title=f"{tm} wordiness by Day",
            data_frame=df, x='NITCH', y=m, facet_col="Day", color='NITCH',
            custom_data=['Puzzle','NITCH','Blogger'],
            orientation='h',
            # plotly wont accept spacing = 0
            facet_col_spacing=0.001, facet_row_spacing=0.001,
            #color_discrete_sequence=colour_snITCH
            color_continuous_scale=colour_snitch_cont
            )
        
        # Some of this formatting needs to be environment sensitive: Mobile vs Desktop
        fig.update_traces(
            hovertemplate=xword_hover([('Puzzle',0),('Count','x'),('NITCH',1),('Blogger',2)]),
            marker=marker,
            selector=dict(mode='markers')
            )
        fig.update_layout(
            showlegend=False
            )
        # Shared layout settings for all these charts
        xword_layout(fig)
        
        # With multiple facets doing this in update_layout only applies to the 1st
        fig.update_xaxes(dict(fixedrange=True, visible=False, showticklabels=False))
        fig.update_yaxes(dict(fixedrange=True))
        
        # Continuous scale for NITCH OTT in mobile mode
        fig.update_coloraxes(showscale=showscale)
        
        # Edit the facet annotations to remove the "Day=" bit
        for a in fig.layout.annotations:
            a.text = a.text.split("=")[1]

        # Add a median marker line
        # Have to do per facet
        for dno in df['dno'].unique():
            # Need to calc Median for just this Day
            day = df.loc[df['dno'] == dno]
            med = np.median(day[m])
            fig.add_hline(y=med, line_dash="dot", row="all", col=dno,
                          annotation_text="Median", 
                          annotation_position="bottom right"
                         )

        figs[m] = fig
        # End of Measures loop
        
    return figs

# End of wc_x_dow -------------------------------------------------------------

def wc_witch_v_nitch(df, meas=xwd.wc_meas, **kwargs):
    # Optional parameters
    dev = kwargs.get('device', None)
    # Setting markers like this breaks hovertemplate!!!
    #data_values = ['SNITCH', 'WITCH', 'WITCH-F']
    #color_map = {'SNITCH': 'blue', 'WITCH-F': 'red', 'WITCH': 'green'}
    #colors = [color_map[value] for value in data_values]
    
    # layout_by_device. Too bespoke to each chart to share
    # Too many markers in this one to make them big
    # Default = desktop
    marker = dict(size=6)
    legend = dict(orientation='v',itemsizing='constant')

    match dev:
        case 'tablet':
            marker = dict(size=4)
        case 'mobile':
            marker = dict(size=3)
            # anchor top/bottom refers to the t/b of the legend, not the plot
            legend = dict(orientation='h', itemsizing='constant',
                          yanchor='top', y=-0.2, xanchor='left'
                          )
            
    # This would have been easier in SQL but I need to learn
    # Measures all use same Y-axis of NITCH but we want them
    # Split df into 3 traces 1 per measure: NITCH, PITCH, WITCH
    # We also need the actual NITCH for hover data
    # NOTE: Never updating the original df object
    dfn = df[meas+['NITCH','Puzzle','Blogger']]
    dfp = df[meas+['PITCH','Puzzle','Blogger','NITCH']]
    dfw = df[meas+['WITCH','Puzzle','Blogger','NITCH']]
    # Add Trace column so we can split into Color/Facet giving each its own trendline
    dfn['Trace'] = 'NITCH'
    dfp['Trace'] = 'PITCH'
    dfw['Trace'] = 'WITCH'
    # Need 1 colname which is constant over all which is the one we will plot + the actual
    dfp.rename(columns={'NITCH':'aNITCH','PITCH':'NITCH'}, inplace=True)
    dfw.rename(columns={'NITCH':'aNITCH','WITCH':'NITCH'}, inplace=True)
    dfn['aNITCH'] = dfn['NITCH']
    # Add Errors. NITCH = NITCH so these will overwrite the actual NITCH marker. Thats OK
    dfe = dfp.loc[dfp['NITCH'].isna()]
    dfe['Trace'] = 'Errors'
    dfe['NITCH'] = dfe['aNITCH']
    #dfpe['NITCH'] = dfpe['NITCH'] * 1.5
    # Union them all together. Uses colname not position
    dfu = pd.concat([dfn, dfp, dfw, dfe ]) 
    # Cap everything at 250, the outliers are stretching the graph
    dfu.loc[dfu['NITCH'] > 250, 'NITCH'] = 250
    #print(dfu)
    #raise Exception("STOP")
        
    figs = {}

    for m in meas:
        # Basic plot
        # Still dont like this, not clear enough. The green doesn't work
        fig = px.scatter(
            title="Solver WITCH vs Puzzle NITCH",
            data_frame=dfu, x=m, y='NITCH', color='Trace',
            color_discrete_sequence=['DarkGray','Gold','MediumSeaGreen','OrangeRed'],
            custom_data=['Trace','Puzzle','Blogger','aNITCH'],
            trendline='ols'
            )

        fig.update_traces(
            hovertemplate = xword_hover([(None,0),('Puzzle',1),('NITCH',3),('This','y')]),
            # Want these small, its the trendline we need to see
            #marker=layout['marker'],
            marker=marker,
            selector=dict(mode='markers') #,color=colors)
            )
        fig.update_layout(
            legend=legend
            )
        
        # Making the trendlines thicker is hard work
        # I only really want to highlight WITCH
        tlines=[]
        for k, trace in enumerate(fig.data):
            if trace.mode is not None and trace.mode == 'lines' and trace.name == 'WITCH':
                tlines.append(k)
        #print(tlines)
        for id in tlines:
            fig.data[id].update(line_width=3)
    
        # Apply shared layout settings for all these charts
        xword_layout(fig)
        
        figs[m] = fig

    return figs

# End of wc_wITCH_v_nITCH -------------------------------------------------------------

# For testing charts without deployment env
def test():
    # Getting the df is trivial, get both
    df = xwd.get_wc_x_puzzle_data()
    dfw = xwd.get_witch_v_nitch_data()
    figs = wc_x_puzzle(df, ['ClueWC'], device='mobile')
    #figs = wc_x_dow(df, ['ClueWC'], device='mobile')
    #figs = wc_witch_v_nitch(dfw, ['ClueWC'], device='mobile')
    
    for fig in figs.values(): fig.show(config={'displayModeBar': False})
    
# End of test

# Run this module alone to test
#test()