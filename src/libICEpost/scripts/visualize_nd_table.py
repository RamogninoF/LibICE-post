#!/usr/bin/env python3
"""
Visualize a tabulation for LibICE-OpenFOAM code.

Compatible with LibICE-8.
"""

#--------------------------------------------#
#                   Imports                  #
#--------------------------------------------#

import pandas as pd
from dash import Output, Input, Dash, dcc, html
import numpy as np
import plotly.graph_objects as go
import webbrowser
from waitress import create_server

import argparse
import traceback
import logging
from libICEpost.src.base.dataStructures.Tabulation.OFTabulation import OFTabulation
from libICEpost.src.base.Functions.runtimeWarning import enf

log = logging.getLogger("createPremixedChemistryTable")

#--------------------------------------------#
#              Argument parsing              #
#--------------------------------------------#
def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    #Control dictionary
    p.add_argument("tablePath",
                   help="The path where the tabulation is stored", type=str)
    
    #Debugging?
    # Redirect debug
    p.add_argument("-debug", action="store_true",
                   help="Debugging?")

    return(p.parse_args())

#--------------------------------------------#
#                   Logging                  #
#--------------------------------------------#
#Formatter for logging
class MyFormatter(logging.Formatter):
    info_fmt = "%(msg)s"
    debug_fmt = enf(enf("DEBUG", "warning"),"bold") + " [%(module)s:%(lineno)s]: %(msg)s"
    err_fmt = enf(enf("ERROR", "fail"),"bold") + ": %(msg)s"
    warning_fmt = enf(enf("WARNING", "fail"),"warning") + ": %(msg)s"
    
    def _update(self,string:str):
        self._fmt = string
        self._style._fmt = string
    
    def format(self, record):
        
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Info
        if record.levelno == logging.INFO:
            self._update(self.info_fmt)
        if record.levelno == logging.DEBUG:
            self._update(self.debug_fmt)
        if record.levelno == logging.ERROR:
            self._update(self.err_fmt)
        if record.levelno == logging.WARNING:
            self._update(self.warning_fmt)

        # Call the original formatter class to do the grunt work
        result = super().format(record)

        # Restore the original format configured by the user
        self._update(format_orig)

        return result


#--------------------------------------------#
#                 making app                 #
#--------------------------------------------#

def makeApp(tablePath:str):
    table = OFTabulation.fromFile(path=tablePath)
    log.debug("Loaded table")

    data = table.toPandas()
    log.debug("Converted to pandas")

    if not "completed" in data:
        data["completed"] = True

    #The app
    app = Dash(__name__)

    #Axes, ranges, variables
    axis = table.order
    ranges = table.ranges
    variables = table.fields

    app.layout = html.Div([
        # Left container for dropdowns and slider
        html.Div(
        [
            # Dropdowns for variable
            html.Div([
                html.Label('Variable:'),
                dcc.Dropdown(id='variable-dropdown', options=[{'label': f, 'value': f} for f in variables], value=variables[0]),
            ], style={'width': '100%', 'marginBottom': '10px'}),
            # Dropdowns for X, Y, Z axes
            html.Div([
                html.Label('X-axis:'),
                dcc.Dropdown(id='xaxis-dropdown', options=[{'label': ax, 'value': ax} for ax in axis], value=axis[0]),
            ], style={'width': '100%', 'marginBottom': '10px'}),

            html.Div([
                html.Label('Y-axis:'),
                dcc.Dropdown(id='yaxis-dropdown', options=[{'label': ax, 'value': ax} for ax in axis], value=axis[1]),
            ], style={'width': '100%', 'marginBottom': '10px'}),

            html.Div([
                html.Label('Z-axis:'),
                dcc.Dropdown(id='zaxis-dropdown', options=[{'label': ax, 'value': ax} for ax in axis], value=axis[2]),
            ], style={'width': '100%', 'marginBottom': '10px'}),
        ]
        +
        # Dropdown and Slider for other dimensions
        [
            html.Div([
                    html.Label('Slice along:'),
                    dcc.Dropdown(id=f"slice-dropdown{ii}", options=[{'label': ax, 'value': ax} for ax in axis], value=axis[ii]),
                    dcc.Slider(id=f"slice-slider{ii}", min=0, max=0, step=1, value=0, marks={}),
            ], style={'width': '100%', 'marginBottom': '10px'})
            for ii in range(3,len(axis))
        ]
        +
        [
            # RadioItems for completed filter
            html.Div([
                html.Label('Completion Status:'),
                dcc.RadioItems(
                    id='completion-filter',
                    options=[
                        {'label': 'Completed', 'value': 'completed'},
                        {'label': 'Not Completed', 'value': 'not_completed'},
                        {'label': 'Both', 'value': 'both'}
                    ],
                    value='completed',  # Default to 'Completed'
                    inline=True
                )
            ], style={'width': '100%', 'marginBottom': '10px'}),
        ], style={'width': '25%', 'padding': '20px', 'display': 'flex', 'flexDirection': 'column'}),

        # Right container for the graph
        html.Div([
            # 3D Scatter Plot
            dcc.Graph(id='3d-scatter-plot', style={'height': '100vh', 'width': '100%'})
        ], style={'width': '80%', 'padding': '10px'})
    ], style={'display': 'flex', 'height': '100vh'})


    @app.callback(
        *[[Output(f"slice-slider{ii}", 'min'),
        Output(f"slice-slider{ii}", 'max'),
        Output(f"slice-slider{ii}", 'marks'),
        Output(f"slice-slider{ii}", 'value')] for ii in range(3,len(axis))],
        *[Input(f"slice-dropdown{ii}", 'value') for ii in range(3,len(axis))]
    )
    def update_slice_slider(*slice_axis):
        out = [[0, len(ranges[ax]) - 1, {i: str(v) for i, v in enumerate(ranges[ax])}, 0] for ax in slice_axis]
        outList = []
        for v in out:
            outList += v
        return outList

    @app.callback(
        Output('3d-scatter-plot', 'figure'),
        [Input('variable-dropdown', 'value'),
        Input('xaxis-dropdown', 'value'),
        Input('yaxis-dropdown', 'value'),
        Input('zaxis-dropdown', 'value')]
        +
        [Input(f"slice-dropdown{ii}", 'value') for ii in range(3,len(axis))]
        +
        [Input(f"slice-slider{ii}", 'value') for ii in range(3,len(axis))]
        +
        [Input('completion-filter', 'value')]  # Add the completion filter as an input
    )
    def update_graph(variable, xaxis, yaxis, zaxis, *args):
        slice_axis = args[:((len(args)-1) // 2)]
        slice_idx = args[((len(args)-1) // 2):(len(args)-1)]
        completed_filter = args[-1]
        
        # Ensure all axes are unique
        if len({xaxis, yaxis, zaxis, *slice_axis}) < 4:
            return go.Figure()
        waxis = [x for x in axis if x not in [xaxis, yaxis, zaxis]]

        # Filter data based on slice and completion status
        if completed_filter == 'completed':
            subData = data[data["completed"] == True]
        elif completed_filter == 'not_completed':
            subData = data[data["completed"] == False]
        else:  # Both
            subData = data
        
        for ii, ax in enumerate(waxis):
            subData = subData[data.loc[:, ax] == ranges[ax][slice_idx[ii]]]

        hover_template = (
            f'<b>{xaxis}</b>:'+'%{customdata[0]}<br>'+
            f'<b>{yaxis}</b>:'+'%{customdata[1]}<br>'+
            f'<b>{zaxis}</b>:'+'%{customdata[2]}<br>'+
            f"".join([f'<b>{ax}</b>: {ranges[ax][slice_idx[ii]]}<br>' for ii, ax in enumerate(waxis)])+
            f'<extra></extra>'
        )
        # Create 3D scatter plot
        fig = go.Figure(data=go.Scatter3d(
            x=subData[xaxis],
            y=subData[yaxis],
            z=subData[zaxis],
            mode='markers',
            marker=dict(
                size=5,
                color=subData[variable],
                colorscale='turbo',
                colorbar=dict(title=variable),
                opacity=0.8
            ),
            customdata=np.stack([subData[xaxis], subData[yaxis], subData[zaxis]], axis=-1),
            hovertemplate=hover_template
        ))
        fig.update_layout(
            scene=dict(
                xaxis_title=xaxis,
                yaxis_title=yaxis,
                zaxis_title=zaxis,
            ),
            title=variable
        )
        return fig
    
    return app

#--------------------------------------------#
#                     Main                   #
#--------------------------------------------# 
#Main
def main() -> None:
    try:
        #Parsing
        args = cmdline_args()
        
        #Logging
        hdlrs = []
        
        #stdout
        hdlr = logging.StreamHandler()
        hdlr.setFormatter(MyFormatter())
        hdlr.setLevel("DEBUG" if args.debug else "INFO")
        
        hdlrs.append(hdlr)
        logging.basicConfig(level="DEBUG" if args.debug else "INFO",handlers=hdlrs)
        
        #Running the program
        app = makeApp(args.tablePath)
        
        host = "127.0.0.1"
        server = create_server(app.server, host=host, port=0)
        log.info("Running app on: " + f"http://{server.getsockname()[0]}:{server.getsockname()[1]}/")
        webbrowser.open_new(f"http://{server.getsockname()[0]}:{server.getsockname()[1]}/")
        server.run()
        
    except BaseException as err:
        if not isinstance(err,SystemExit):
            print(f'Failed generation of table: {err}')
            print(traceback.format_exc())

if __name__ == '__main__':
    main()