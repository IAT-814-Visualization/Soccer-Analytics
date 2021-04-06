import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import dash_cytoscape as cyto
import copy
import pandas as pd
import numpy as np
from flask import Flask
pd.set_option("mode.chained_assignment", None)

# Parent Club
parent_club = "Manchester United"

# # Pass types in filter should be passed here
#pass_names = ["Long Pass", "Short Pass"]

##########################################################
# File Operations
##########################################################
### Reading player position based on matched
global pos_df
pos_df = pd.read_excel('nodepos.xlsx',sheet_name='final_player_list')

# ClubNames in filter should be passed here
club_names = pos_df.sort_values('teamName')['teamName'].unique().tolist()
club_names = [i for i in club_names if i != 'Manchester United']

### Reading the passing data
global pass_df
pass_df = pd.read_csv('pass_network.csv')
#print(pass_df.columns)
def time_cat(x):
    if x >= 0 and x <= 15:
        return '0-15'
    elif x > 15 and x <= 30:
        return '16-30'
    elif x > 30 and x <= 45:
        return '31-45'
    elif x > 45 and x <= 60:
        return '45-60'
    elif x > 60 and x <= 75:
        return '61-75'
    else:
        return '76-90+'
pass_df['timeCat'] = pass_df['eventSec'].apply(lambda x: time_cat(x))


### Pass Types
global pass_names
pass_names = pass_df['subEventName'].unique().tolist()
pass_names.append("All Passes")
# print(pass_names)

##################################################################
graph_styles = {
    'light': {
        'bg_color': 'rgb(239, 239, 239)',
        'color': 'rgb(57, 57, 57)',
        'titlefont': {
            'size': 25,
            'family': 'Bebas Neue, Roboto Condensed, Roboto, Helvetica Narrow, Arial Narrow, Helvetica, Arial',
            'color': 'rgb(68, 68, 68)'
        },
        'axis_color': 'rgb(68, 68, 68)',
        'profile_color': 'rgb(80, 80, 80)',
        'legendfont': {
            'color': 'rgb(68, 68, 68)'
        },
        'grid_color': 'rgb(180, 180, 180)'
    },

    'dark': {
        'bg_color': 'rgb(57, 57, 57)',
        'color': 'rgb(239, 239, 239)',
        'titlefont': {
            'size': 25,
            'family': 'Bebas Neue, Roboto Condensed, Roboto, Helvetica Narrow, Arial Narrow, Helvetica, Arial',
            'color': 'rgb(255, 255, 255)'
        },
        'axis_color': 'rgb(180, 180, 180)',
        'profile_color': 'rgb(170, 170, 170)',
        'legendfont': {
            'color': 'rgb(180, 180, 180)'
        },
        'grid_color': 'rgb(100, 100, 100)'
    },

}

field_style = {
    '1': {
        'fill_color': 'rgba(45, 134, 45, 1)',
        'line_color': 'rgba(128, 0, 128, 1)'
    },

    '2': {
        'fill_color': 'rgba(162, 185, 97, 1)',
        'line_color': 'rgba(28, 32, 14, 1)'
    },
}

field_theme = '2'
##################################################################
# Header in the top of the page
def Header(name, app):
    title = html.Div([html.H2(name, style={"margin-top": 5})])
    return dbc.Row([dbc.Col(title, md=7)])


# Defining a card for clubname1
def clubname1(name,app):
    card = dbc.Card(
        [
            # dbc.CardImg(src="/static/images/manu.jpg"),
            html.H4(
                children=[
                    html.Div(name,id='club1_header')
                ]
            ),
            html.H5(
                children=[
                    html.Div(id='pass1_type')
                ]
            )
        ],
        body=False,
        color="gray",
        inverse=True,
    )
    return card


# Defining a card for clubname2
def clubname2(app):
    card = dbc.Card(
        [
            html.H4(
                children=
                [
                    html.Div(id='club2_header')
                ]
            ),
            html.H5(
                children=[
                    html.Div(id='pass2_type')
                ]
            )
        ],
        body=False,
        color="warning",
        inverse=True,
    )
    return card


# Drop down for club selection in second pane.
def club_dropdown(label, app, club_names):
    items = []
    for each in club_names:
        items.append(dbc.DropdownMenuItem(each, id=each))

    dropdown = html.Div(
        [
            dbc.DropdownMenu(id='club_clicks', label=label, children=items, right=True, color='warning'),
            html.P(id="club-clicks", className="club-dn"),
        ]
    )
    return dropdown


# Drop down for pass types
def pass_dropdown(label, app, pass_names):
    items = []
    for each in pass_names:
        items.append(dbc.DropdownMenuItem(each, id=each))

    dropdown = html.Div(
        [
            dbc.DropdownMenu(label=label, children=items, right=True, color='info'),
            html.P(id="pass-clicks", className="pass_dn"),
        ]
    )
    return dropdown


def create_full_field(theme):
    field = {
        'type': 'rect',
        'x0': 0,
        'x1': 100,
        'y0': 0,
        'y1': 100,
        'line': {
            'color': graph_styles[theme]['titlefont']['color']
        },
        'layer': 'below',
        'fillcolor': field_style[field_theme]['fill_color']
    }

    left_penalty = {
        'type': 'rect',
        'y0': 20,
        'y1': 80,
        'x0': 0,
        'x1': 16,
        'line': {
            'color': graph_styles[theme]['titlefont']['color']
        },
        'layer': 'below'
    }

    right_penalty = {
        'type': 'rect',
        'y0': 20,
        'y1': 80,
        'x0': 84,
        'x1': 100,
        'line': {
            'color': graph_styles[theme]['titlefont']['color']
        },
        'layer': 'below'
    }

    left_post = {
        'type': 'rect',
        'y0': 46,
        'y1': 54,
        'x0': 0,
        'x1': -2,
        'line': {
            'color': graph_styles[theme]['titlefont']['color']
        },
        'layer': 'below'
    }

    right_post = {
        'type': 'rect',
        'y0': 46,
        'y1': 54,
        'x0': 100,
        'x1': 102,
        'line': {
            'color': graph_styles[theme]['titlefont']['color']
        },
        'layer': 'below'
    }

    centre_line = {
        'type': 'line',
        'y0': 0,
        'y1': 100,
        'x0': 50,
        'x1': 50,
        'line': {
            'color': graph_styles[theme]['titlefont']['color']
        },
        'layer': 'below'
    }

    full_field_shapes = [field, left_penalty, right_penalty,centre_line, left_post, right_post]

    # duplicate_shapes = []
    # for shape in full_field_shapes:
    #     new_shape = copy.deepcopy(shape)
    #     new_shape['xref'] = 'x2'
    #     new_shape['yref'] = 'y2'
    #     duplicate_shapes.append(new_shape)

    #full_field = full_field_shapes + duplicate_shapes
    return full_field_shapes


full_field = {'dark': create_full_field('dark'), 'light': create_full_field('light')}

def create_pos(positions_df):

    formation_team = go.Scatter(
        x=positions_df.X.values.tolist(),
        y=positions_df.Y.values.tolist(),
        name=str(positions_df['gameweek'].unique()[0]),
        mode='markers',
        marker={
            'size': 40,
            ## color coding required for pass density
            'color': 'red',
            'opacity': 1
        },
        textfont={
           'color': 'white',
           #                                     'family': 'LOVES',
           #                                     'size': 30
        },
        textposition='bottom center',
        text="Name :" + positions_df.shortName.astype('str') + "<br>    Position: " + positions_df.position.astype('str'),
        customdata=positions_df.shortName,
        hoverinfo='text',
    )

    return formation_team

def create_pass_line(pass_net):

    pass_net_agg = pass_net\
        .groupby(['matchId','teamId','playerId_sender','shortName_sender','position_sender', 'X_sender', 'Y_sender',
                      'playerId_receiver','shortName_receiver','position_receiver', 'X_receiver', 'Y_receiver'])\
        .agg({'Label':'count'})\
        .reset_index().rename(columns={'Label':'Pass_count'})

    #print(pass_net_agg.head())
    line_team = []
    for idx, row in pass_net_agg.iterrows():
        trace = go.Scatter(
                        x = [row['X_sender'], row['X_receiver']],
                        y = [row['Y_sender'], row['Y_receiver']],
                        mode = 'lines',
                        line = {
                                'width': 5 * (row['Pass_count'] / pass_net_agg['Pass_count'].max()),
                                'color': 'black'
                            },
                        showlegend = False,
                        opacity = (row['Pass_count'] /  pass_net_agg['Pass_count'].max().max()),
                        text = 'Number of Passes: {}'.format(row['Pass_count']),
                        hoverinfo = 'text',
                        # xaxis = 'x2' if team == 'away' else 'x',
                        # yaxis = 'y2' if team == 'away' else 'y',
                        )
        line_team.append(trace)
    return line_team


def create_passing_network_map(last_match_df,pass_net,theme,opponent_flag):

    pos_traces = create_pos(last_match_df)
    pass_traces = create_pass_line(pass_net)

    data = [pos_traces] + pass_traces

    layout = {
        'shapes': full_field[theme],
        'hovermode': 'closest',
        'xaxis': {'range': [-5, 105], 'visible': False},
        'yaxis': {'range': [0, 100], 'visible': False},
        'xaxis2': {'range': [105, -5], 'visible': False},
        'yaxis2': {'range': [100, 0], 'visible': False},
        'plot_bgcolor': graph_styles[theme]['bg_color'],
        'paper_bgcolor': graph_styles[theme]['bg_color'],
        #'width' : 850,
        #'height': 850,
        'showlegend': False,
        'legend' :dict(
                        orientation="h",
                        yanchor="bottom",
                        #y=1.02,
                        xanchor="right"),
                        #x=1),
        'dragmode': 'select',
        'margin': {
            'l': 0,
            'r': 0,
            't': 0,
            'b': 0,
        },
        'titlefont': {
            #                     'size': 20,
            #                     'family': 'ObelixPro',
            'color': graph_styles[theme]['legendfont']['color']
        },
        #     'title': '{}'.format(events.loc[0,'team']['name'])
    }

    fig = go.Figure(data=data, layout=layout)
    if opponent_flag == 'y':
        xval = 0.54
        yval = 5
        axval = 0.65
        ayval = 5
    else:
        xval = 0.46
        yval = 5
        axval = 0.35
        ayval = 5

    fig.add_annotation(
        xref="x domain",
        yref="y",
        x=xval,
        y=yval,
        text="ATTACK",
        # If axref is exactly the same as xref, then the text's position is
        # absolute and specified in the same coordinates as xref.
        axref="x domain",
        # The same is the case for yref and ayref, but here the coordinates are data
        # coordinates
        ayref="y",
        ax=axval,
        ay=ayval,
        arrowhead=5,
    )
    return fig
    #return data,layout,full_field[theme]

def create_passing_bars(pass_net):
    pass_net_agg = pass_net\
        .groupby(['matchId','teamId','timeCat'])\
        .agg({'Label':'count'})\
        .reset_index().rename(columns={'Label':'Pass_count'})

    print(pass_net_agg)
    fig = px.bar(pass_net_agg, x="timeCat", y="Pass_count",labels={'Pass_count':'Number of passes','timeCat':'Minutes Played'})
    return fig

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.LUX])
# Initializing pitch plotter


app.layout = dbc.Container(
    [
        Header("Soccer Event Analytics", app),
        html.Button(id='theme_switcher'),
        html.Hr(),
        html.Div(id="dashboard-body",children=
            [
                dbc.Row(
                    [
                        dbc.Col(pass_dropdown("Select a pass type", app, pass_names), align="start"),
                        dbc.Col(club_dropdown("Select opposition club", app, club_names), align="end"),
                    ],
                    justify="end",
                ),
                dbc.Row(
                    [
                        # Pane 1 - Clubname card display. Fixed to Manchester united for now
                        dbc.Col(clubname1(parent_club,app), align="start", width=6),
                        dbc.Col(clubname2(app), align="end", width=6),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id='pass_map1',config={'modeBarButtons': [['select2d','lasso2d','resetViews']], 'displaylogo':False,'displayModeBar': True}), align="center", width=6),
                        dbc.Col(dcc.Graph(id='pass_map2', config={'modeBarButtons': [['select2d','lasso2d','resetViews']], 'displaylogo':False,'displayModeBar': True}), align="end", width=6),
                    ]
                ),
                dbc.Row(
                    [
                       dbc.Col(dcc.Graph(id='pass_bar1'),align="start",width=6),
                       dbc.Col(dcc.Graph(id='pass_bar2'),align="end",width=6)
                    ]
                ),
            ],
        ),
        html.Div(id='theme_div', style={'display': 'none'}),
    ],
    fluid=True,
)


# @app.route('/')
# def hello_world():
#    return 'Hello World!'

@app.callback(
            Output('theme_switcher', 'children'),
            [Input('theme_switcher', 'n_clicks')])
def switch_theme(n_clicks):
    if (not n_clicks) or (n_clicks%2 == 0):
        button_text = 'SWITCH TO DARK THEME'
    else:
        button_text = 'SWITCH TO LIGHT THEME'
    return button_text


@app.callback(
            Output('theme_div', 'children'),
            [Input('theme_switcher', 'n_clicks')])
def update_theme(n_clicks):
    if (not n_clicks) or (n_clicks%2 == 0):
        theme = 'light'
    else:
        theme = 'dark'
    return theme

@app.callback(
    Output('club2_header', 'children'),
    [Input('AFC Bournemouth', 'n_clicks'),Input('Crystal Palace', 'n_clicks'),
     Input('Arsenal', 'n_clicks'),Input('Southampton', 'n_clicks'),
     Input('Brighton & Hove Albion', 'n_clicks'),Input('Huddersfield Town', 'n_clicks'),
     Input('Chelsea', 'n_clicks'),Input('West Ham United', 'n_clicks'),
     Input('Everton', 'n_clicks'),Input('Liverpool', 'n_clicks'),
     Input('Leicester City', 'n_clicks'),Input('Newcastle United', 'n_clicks'),
     Input('Manchester City', 'n_clicks'),
     Input('Stoke City', 'n_clicks'), Input('Tottenham Hotspur', 'n_clicks'),
     Input('Burnley', 'n_clicks'), Input('Watford', 'n_clicks'),
     Input('Swansea City', 'n_clicks'), Input('West Bromwich Albion', 'n_clicks'),
     ]
)
def update_club_name2(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "Brighton & Hove Albion"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return button_id

@app.callback(
    Output('pass1_type', 'children'),Output('pass2_type', 'children'),
    [Input('Simple pass', 'n_clicks'),Input('High pass', 'n_clicks'),
     Input('Head pass', 'n_clicks'),Input('Smart pass', 'n_clicks'),
     Input('Launch', 'n_clicks'),Input('Hand pass', 'n_clicks'),
     Input('Cross', 'n_clicks'),Input('All Passes', 'n_clicks')]
)
def update_pass_type(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "All Passes"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return button_id,button_id


@app.callback(
    Output('pass_map1', 'figure'),Output('pass_bar1','figure'),
    [Input('club1_header', 'children'),Input('pass1_type', 'children'),
     Input('theme_div', 'children')])
def update_pass_map(club1_name, pass1_type, theme):
    last_week = 37
    last_match_df = pos_df[(pos_df['gameweek'] == last_week) & (pos_df['teamName'] == club1_name)]
    match_id = last_match_df['matchId'].unique()[0]
    team_id = last_match_df['teamId'].unique()[0]
    if pass1_type == 'All Passes':
        pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id)]
    else:
        pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['subEventName'] == pass1_type)]
    print(pass_net.head())

    opponent_flag = 'n'
    pass_network = create_passing_network_map(last_match_df,pass_net,theme,opponent_flag)
    pass_bar = create_passing_bars(pass_net)
    return pass_network,pass_bar
    #return figure

@app.callback(
    Output('pass_map2', 'figure'),Output('pass_bar2','figure'),
    [Input('club2_header', 'children'),
     Input('club1_header', 'children'),Input('pass2_type', 'children'),
     Input('theme_div', 'children')])
def update_pass_map(club2_name,club1_name,pass2_type, theme):
    print("Club Name 2 is ",club2_name)
    last_week = 37
    last_match_df = pos_df[(pos_df['gameweek'] == last_week) & (pos_df['teamName'] == club2_name)]
    last_match_df['X'] = 100 - last_match_df['X']
    last_match_df['Y'] = 100 - last_match_df['Y']
    match_id = last_match_df['matchId'].unique()[0]
    team_id = last_match_df['teamId'].unique()[0]
    if pass2_type == 'All Passes':
        pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id)]
    else:
        pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['subEventName'] == pass2_type)]
    pass_net['X_sender'] = 100 - pass_net['X_sender']
    pass_net['Y_sender'] = 100 - pass_net['Y_sender']
    pass_net['X_receiver'] = 100 - pass_net['X_receiver']
    pass_net['Y_receiver'] = 100 - pass_net['Y_receiver']
    #print(last_match_df.head())
    opponent_flag = 'y'
    pass_network = create_passing_network_map(last_match_df,pass_net,theme,opponent_flag)
    pass_bar = create_passing_bars(pass_net)
    return pass_network,pass_bar

if __name__ == '__main__':
    app.run(debug=true)
