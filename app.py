from __future__ import print_function
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output,State
import pandas as pd
import numpy as np
from flask import Flask
pd.set_option("mode.chained_assignment", None)


# Parent Club
parent_club = "Manchester United"

#Constants for fixing range in yscale of bar plot
xrange = {'Simple pass':180,
 'High pass':50,
 'Head pass':30,
 'Smart pass': 10,
 'Launch': 10,
 'Hand pass': 10,
 'Cross':10,
 'All Passes': 200}

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

### Pass Types
global pass_names
pass_names = pass_df['subEventName'].unique().tolist()
pass_names.append("All Passes")


# Match Results
global match_scores
match_scores = pd.read_csv("Match_Scores.csv")

#Pass Accuracy
global pass_acc
pass_acc = pd.read_csv("pass_accuracy.csv")
pass_acc = pass_acc.rename(columns={"playerId_sender":"playerId"})

##################################################################
# Custom CSS styles
##################################################################
graph_style = {'box-shadow': '2px 2px 2px lightgrey',  'border-radius': '5px',
                    'background-color': '#f9f9f9','margin': '10px','padding': '15px','position': 'relative'}

bar_style = {'box-shadow': '2px 2px 2px lightgrey',
                    'background-color': '#f9f9f9','position': 'relative'}

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
##################################################################
def Header(name, app):
    title = html.Div([
                html.H2(name, style={"margin-top": 5}),

    ])
    return dbc.Row([dbc.Col(title, md=7)])


# Defining a card for clubname1
def clubname1(name,app):
    card = dbc.Card(
        [
            html.H4(
                children=[
                    html.Div(name,id='club1_header'),
                    html.H5(
                        children=[
                            html.Div(id='pass1_type')
                        ]
                    )
                ]
            )
        ],
        body=False,
        color="coral",
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
                    html.Div(id='club2_header',style={'width': '50%','float':'left'}),
                    html.Div(club_dropdown("Select an opposition club", app, club_names), style={"flex-grow": "1"}),
                    html.H5(
                        children=[
                            html.Div(id='pass2_type',style={'width': '50%','float':'left'}),
                        ]
                    )
                ]
            ),
        ],
        body=False,
        color="skyblue",
        inverse=True,
        style={"width":"100%"}
    )
    return card

# Drop down for club selection in second pane.
def club_dropdown(label, app, club_names):
    items = []
    for each in club_names:
        items.append(dbc.DropdownMenuItem(each, id=each))

    dropdown = html.Div(
        [
            dbc.DropdownMenu(id='club_clicks', label=label, children=items,bs_size="md", right=True, color='info',style={'vertical-align': 'top','padding': '0px','height':'10px'}),
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
            dbc.DropdownMenu(label=label, children=items, right=True, color='info',style={"display": "flex", "flexWrap": "wrap"}),
            html.P(id="pass-clicks", className="pass_dn"),
        ]
    )
    return dropdown

# Slider for selecting the previous matches based on week
def week_slider(slider_id,minval,maxval,values):
    card = dbc.Card(
        [
            dbc.CardHeader(html.H5("Select a game week")),
            dbc.CardBody(
                dcc.Slider(
                id = slider_id,
                min=minval,
                max=maxval,
                value=values,
                included=False,
                marks={weeks: weeks for weeks in range(minval, maxval+1)},
                updatemode='mouseup'
                )
            )
        ],style=graph_style
    )
    return card

# Defining the football pitch
def create_full_field():
    field = {
        'type': 'rect',
        'x0': 0,
        'x1': 100,
        'y0': 0,
        'y1': 100,
        'line': {
            'color': 'rgb(68, 68, 68)'
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
            'color': 'rgb(68, 68, 68)'
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
            'color': 'rgb(68, 68, 68)'
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
            'color': 'rgb(68, 68, 68)'
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
            'color': 'rgb(68, 68, 68)'
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
            'color': 'rgb(68, 68, 68)'
        },
        'layer': 'below'
    }

    full_field_shapes = [field, left_penalty, right_penalty,centre_line, left_post, right_post]

    return full_field_shapes


full_field = create_full_field()

# Scatter plot for adding plaer positions as nodes
def create_pos(positions_df):

    formation_team = go.Scatter(
        x=positions_df.X.values.tolist(),
        y=positions_df.Y.values.tolist(),
        mode='markers+text',
        marker={
            'size': 40,
            ## color coding required for pass density
            'color': 'darkslateblue',
            'opacity': 1
        },
        textfont={
           'color': 'white',
        },
        textposition='bottom center',
        text="<b>"+positions_df.position.astype('str') +"</b>",
        hovertext="Name :" + positions_df.shortName.astype('str') + "<br>    Position: " + positions_df.position.astype('str'),
        customdata=positions_df[['playerId','matchId']],
        hoverinfo='text',
        showlegend=True,
        legendgroup="group",
        name="players",
    )

    return formation_team

#Defining edges as lines between player positions/nodes
def create_pass_line(pass_net):

    pass_net_agg = pass_net\
        .groupby(['matchId','teamId','playerId_sender','shortName_sender','position_sender', 'X_sender', 'Y_sender',
                      'playerId_receiver','shortName_receiver','position_receiver', 'X_receiver', 'Y_receiver'])\
        .agg({'Label':'count'})\
        .reset_index().rename(columns={'Label':'Pass_count'})

    line_team = []
    for idx, row in pass_net_agg.iterrows():
        trace1 = go.Scatter(
            x=[(row['X_sender'] + row['X_receiver']) / 2] ,
            y=[(row['Y_sender'] + row['Y_receiver']) / 2] ,
            mode = 'markers',
            marker_size = 0.5,
            text= 'Number of Passes: {}'.format(row['Pass_count']),
            hoverinfo = 'text',
            marker={'opacity':0},
            hoverlabel={'bgcolor':"white"}
        )
        trace2 = go.Scatter(
                        x = [row['X_sender'], row['X_receiver']],
                        y = [row['Y_sender'], row['Y_receiver']],
                        mode = 'lines',
                        line = {
                                'width': 5 * (row['Pass_count'] / pass_net_agg['Pass_count'].max()),
                                'color': 'black'
                            },
                        showlegend = True,
                        legendgroup="group",
                        name="pass lines",
                        opacity = (row['Pass_count'] /  pass_net_agg['Pass_count'].max()),
                        text = 'Number of Passes: {}'.format(row['Pass_count']),
                        customdata=[row['Pass_count']],
                        hoverinfo = 'text',
                        )
        line_team.append(trace1)
        line_team.append(trace2)
    return line_team

#Combining nodes and edges to form a pass network map
def create_passing_network_map(last_match_df,pass_net,opponent_flag):

    pos_traces = create_pos(last_match_df)
    pass_traces = create_pass_line(pass_net)

    data = [pos_traces] + pass_traces

    layout = {
        'shapes': full_field,
        'hovermode': 'closest',
        'xaxis': {'range': [-5, 105], 'visible': False},
        'yaxis': {'range': [0, 100], 'visible': False},
        'xaxis2': {'range': [105, -5], 'visible': False},
        'yaxis2': {'range': [100, 0], 'visible': False},
        'plot_bgcolor': 'rgb(239, 239, 239)',
        'paper_bgcolor': 'rgb(239, 239, 239)',
        #'width' : 885,
        'height': 400,
        'showlegend': False,
        'clickmode' : 'event+select',
        'dragmode': 'select',
        'margin': {
            'l': 0,
            'r': 0,
            't': 0,
            'b': 0,
        },
        'titlefont': {
            'color': 'rgb(68, 68, 68)'
        },
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

# Bar graph to plot the pass aggregate split between timezones
def create_passing_bars(pass_net,passtype,flag):
    if flag == "y":
        pass_net_agg = pass_net \
            .groupby(['matchId', 'teamId', 'timeCat','playerId_sender','shortName_sender']) \
            .agg({'Label': 'count'}) \
            .reset_index().rename(columns={'Label': 'Pass_count','shortName_sender':"Player Name"})

        fig = px.bar(pass_net_agg, x="timeCat", y="Pass_count",color="Player Name", text='Pass_count',
                     labels={'Pass_count': 'No: of completed passes', 'timeCat': 'Game Time'},
                     custom_data=['playerId_sender'],
                     )
    else:
        pass_net_agg = pass_net \
            .groupby(['matchId', 'teamId', 'timeCat']) \
            .agg({'Label': 'count'}) \
            .reset_index().rename(columns={'Label': 'Pass_count'})
        fig = px.bar(pass_net_agg, x="timeCat", y="Pass_count", text='Pass_count',
                     labels={'Pass_count': 'No: of completed passes', 'timeCat': 'Game Time'},
                     custom_data=['timeCat'],
                     )
        fig.update_layout(yaxis={'range': [0, xrange[passtype]]})

    fig.update_layout(xaxis={'tickvals': ['0-15', '16-30', '31-45', '46-60','61-75','76-90+'],'tickmode' : 'array'},clickmode='event+select')
    fig.update_layout(title = {'text':'<b>Completed Pass Distribution during Game</b>','x':0.5,'xanchor': 'center','yanchor': 'top','font_size':15},height=300)
    return fig,pass_net_agg

# Bar graph to plot the inaccurate pass aggregate split between timezones
def create_inaccurate_pass_bars(pass_acc, passtype, flag):
    pass_acc_agg = pass_acc\
        .groupby(['matchId','teamId','timeCat'])\
        .agg({'not accurate':'sum'})\
        .reset_index().rename(columns={'Label':'not accurate'})
    fig = px.bar(pass_acc_agg, x="timeCat", y="not accurate", text='not accurate',
                 labels={'not accurate': 'No: of incomplete passes', 'timeCat': 'Game Time'},
                 custom_data=['timeCat'],
                 )
    if flag == "y":
        pass_acc_agg = pass_acc \
            .groupby(['matchId', 'teamId', 'timeCat','playerId','shortName_sender']) \
            .agg({'not accurate': 'sum'}) \
            .reset_index().rename(columns={'Label': 'not accurate','shortName_sender':"Player Name"})
        fig = px.bar(pass_acc_agg, x="timeCat", y="not accurate", color="Player Name", text='not accurate',
                     labels={'not accurate': 'No: of incomplete passes', 'timeCat': 'Game Time'},
                     custom_data=['playerId'],
                     )

    fig.update_layout(xaxis={'tickvals': ['0-15', '16-30', '31-45', '46-60','61-75','76-90+'],'tickmode' : 'array'},clickmode='event+select')
    fig.update_layout(title = {'text':'<b>Incomplete Pass Distribution during Game</b>','x':0.5,'xanchor': 'center','yanchor': 'top','font_size':15},height=300)
    return fig,pass_acc_agg

# Defining a KPI card for opponent name for both clubs
def opponent(title,idval):
    card = dbc.CardBody(
        [
            html.H6(title,style={'color':'blue','font-weight':'bold'}),
            html.H4(
                html.Div(id=idval),
            ),
        ],style=graph_style
    )
    return card

# Defining a KPI scorecard for both clubs
def scorecard(title,idval,result):

    card = dbc.CardBody(
        [
            html.H6(title,style={'color':'blue','font-weight':'bold'}),
            html.H4([
                html.Div(id=idval,style={'width': '50%','float':'left'}),
                html.Div(id=result),
            ]),
        ],style=graph_style
    )
    return card

# Defining a KPI pass accuracy both clubs
def passacc(accuracy,idval):
    data = go.Indicator(
            mode="gauge+number",
            value=accuracy,
            number={'suffix': "%"},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Pass Accuracy"},
            align="left",
            gauge={'axis': {'range': [0, 100],'tickwidth': 1,'dtick':25},
                   'steps': [
                       {'range': [0, 50], 'color': "lightsalmon"},
                       {'range': [50, 80], 'color': "khaki"},
                       {'range': [80, 100], 'color': "lightgreen"},
                   ],
                   }
    )
    layout = go.Layout(
        autosize=True,
        height=250,
        margin = {
                      'l': 0,
                      'r': 0,
                      't': 0,
                      'b': 0,
                  },
    )

    fig = go.Figure(data=data, layout=layout)
    return fig

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.LUX])


app.layout = dbc.Container(
    [
        Header("Soccer Event Analytics", app),
        html.Hr(),
        html.Div(id="dashboard-body",children=
            [
                dbc.Row(
                    [
                        dbc.Col(week_slider(slider_id='slider1',minval=33,maxval=37,values=37),width=5,align="start"),
                        dbc.Col(pass_dropdown("Filter here by pass category", app, pass_names), width=2, align="end"),
                        dbc.Col(week_slider(slider_id='slider2',minval=33,maxval=37,values=37),width=5,align="start"),
                    ],
                    no_gutters=True
                ),
                dbc.Row(
                    [
                        dbc.Col(clubname1(parent_club,app), align="start", width=6),
                        dbc.Col(clubname2(app), align="start", width=6),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id='pass_map1',config={'modeBarButtons': [['select2d','lasso2d','resetViews']], 'displaylogo':False,'displayModeBar': True}), align="start", width=6,style=bar_style),
                        dbc.Col(dcc.Graph(id='pass_map2', config={'modeBarButtons': [['select2d','lasso2d','resetViews']], 'displaylogo':False,'displayModeBar': True}), align="start", width=6,style=bar_style),
                    ]
                ),
                dbc.Row(
                    [
                       dbc.Col(
                           [
                               dcc.Graph(id='passacc1'),
                               opponent("Opponent","opponent1"),
                               scorecard("Scorecard","scorecard1","result1"),
                        ],align="start", width=2,
                       ),
                       dbc.Col(
                           [
                               dcc.Graph(id='pass_bar1',config={'modeBarButtons': [['select2d','lasso2d','resetViews']], 'displaylogo':False,'displayModeBar': True}),
                               dcc.Graph(id='inac_bar1',config={'modeBarButtons': [['select2d','lasso2d','resetViews']], 'displaylogo':False,'displayModeBar': True}),
                            ],align="start",width=4,style=bar_style,
                        ),
                       dbc.Col(
                           [
                               dcc.Graph(id='pass_bar2',config={'modeBarButtons': [['select2d','lasso2d','resetViews']], 'displaylogo':False,'displayModeBar': True}),
                               dcc.Graph(id='inac_bar2',config={'modeBarButtons': [['select2d', 'lasso2d', 'resetViews']],'displaylogo': False, 'displayModeBar': True}),
                            ],align="start",width=4,style=bar_style
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(id='passacc2'),
                                opponent("Opponent", "opponent2"),
                                scorecard("Scorecard", "scorecard2","result2"),
                            ], align="start", width=2,
                        )
                    ]
                ),
            ],
        ),
    ],
    fluid=True,
)


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
    Output('pass_map1', 'figure'),Output('pass_bar1','figure'),Output('passacc1','figure'),Output('inac_bar1','figure'),
    [Input('club1_header', 'children'),
     Input('pass1_type', 'children'),
     Input('slider1','value'),
     Input('pass_map1','selectedData'),
     Input('pass_bar1','selectedData'),
     Input('inac_bar1','selectedData')],
    [State('pass_bar1','figure'),
     State('inac_bar1','figure')])
def update_pass_map(club1_name, pass1_type,slider1,selectedData,barclickData,inac_click_data,pass_bar,inac_bar):

    pass_player_flag = "n"
    last_week = slider1
    last_match_df = pos_df[(pos_df['gameweek'] == last_week) & (pos_df['teamName'] == club1_name)]
    match_id = last_match_df['matchId'].unique()[0]
    team_id = last_match_df['teamId'].unique()[0]
    if (selectedData is None) and (barclickData is None) and (inac_click_data is None):
        if pass1_type == 'All Passes':
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id)]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id)]
        else:
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['subEventName'] == pass1_type)]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id) & (pass_acc['subEventName'] == pass1_type)]
    elif selectedData is not None:
        pass_player_flag = "y"
        points = selectedData['points']
        playerId = []
        matchId = []
        for item in points:
            if 'customdata' in item:
                playerId.append(item['customdata'][0])
                matchId.append(item['customdata'][1])

        if barclickData is not None:
            pass_player_flag = "y"
            points = barclickData['points']
            time_categories = []
            player_sender_id = []
            for item in points:
                time_categories.append(item['x'])
                player_sender_id.append(item['customdata'][0])

            if '-' in str(player_sender_id[0]):
                player_sender_id = playerId[:]

            if pass1_type == 'All Passes':
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId)) & (pass_df['timeCat'].isin(time_categories)) & (pass_df['playerId_sender'].isin(player_sender_id))]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId)) & (pass_acc['timeCat'].isin(time_categories)) & (pass_acc['playerId'].isin(player_sender_id))]
            else:
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId)) & (
                            pass_df['subEventName'] == pass1_type) & (pass_df['timeCat'].isin(time_categories)) & (pass_df['playerId_sender'].isin(player_sender_id))]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId)) & (
                        pass_acc['subEventName'] == pass1_type) & (pass_acc['timeCat'].isin(time_categories)) & (pass_acc['playerId'].isin(player_sender_id))]
        else:
            if pass1_type == 'All Passes':
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId))]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId))]
            else:
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId)) & (
                            pass_df['subEventName'] == pass1_type)]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId)) & (
                        pass_acc['subEventName'] == pass1_type)]
    else:
        points = barclickData['points']
        time_categories = []
        for item in points:
            time_categories.append(item['x'])
        if pass1_type == 'All Passes':
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['timeCat'].isin(time_categories))]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id) & (pass_acc['timeCat'].isin(time_categories))]
        else:
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['timeCat'].isin(time_categories)) & (
                        pass_df['subEventName'] == pass1_type)]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id) & (pass_acc['timeCat'].isin(time_categories)) & (
                        pass_acc['subEventName'] == pass1_type)]


    opponent_flag = 'n'

    pass_network = create_passing_network_map(last_match_df,pass_net,opponent_flag)

    if barclickData is None:
        pass_bar,ac_df = create_passing_bars(pass_net,pass1_type,pass_player_flag)
        inac_bar,inac_df = create_inaccurate_pass_bars(df_acc,pass1_type,pass_player_flag)

        per_df = ac_df.merge(inac_df,on=["matchId","teamId"]).groupby(["matchId","teamId"]).agg({"not accurate":"sum","Pass_count":"sum"}).reset_index()
        per_df["accuracy"] = (per_df["Pass_count"] / (per_df["not accurate"] + per_df['Pass_count'])) * 100
        accuracy = round(per_df["accuracy"].mean(), 2)
    else:
        ac_df = pass_net \
            .groupby(['matchId', 'teamId', 'timeCat']) \
            .agg({'Label': 'count'}) \
            .reset_index().rename(columns={'Label': 'Pass_count'})
        if pass_player_flag == "y":
            ac_df = pass_net \
                .groupby(['matchId', 'teamId', 'timeCat', 'playerId_sender', 'shortName_sender']) \
                .agg({'Label': 'count'}) \
                .reset_index().rename(columns={'Label': 'Pass_count'})
        inac_df = pass_acc \
            .groupby(['matchId', 'teamId', 'timeCat']) \
            .agg({'not accurate': 'sum'}) \
            .reset_index().rename(columns={'Label': 'not accurate'})
        if pass_player_flag == "y":
            inac_df = pass_acc \
                .groupby(['matchId', 'teamId', 'timeCat', 'playerId', 'shortName_sender']) \
                .agg({'not accurate': 'sum'}) \
                .reset_index().rename(columns={'Label': 'not accurate'})
        per_df = ac_df.merge(inac_df).groupby(["matchId","teamId"]).agg({"not accurate":"sum","Pass_count":"sum"}).reset_index()
        per_df["accuracy"] = (per_df["Pass_count"] / (per_df["not accurate"] + per_df['Pass_count'])) * 100
        accuracy = round(per_df["accuracy"].mean(), 2)
    acc_gauge = passacc(accuracy, "passacc1")
    return pass_network,pass_bar,acc_gauge,inac_bar

@app.callback(
    Output('pass_map2', 'figure'),
    Output('pass_bar2','figure'),Output('passacc2','figure'),Output('inac_bar2','figure'),
    [Input('club2_header', 'children'),
     Input('club1_header', 'children'),
     Input('pass2_type', 'children'),
     Input('slider2','value'),
     Input('pass_map2','selectedData'),
     Input('pass_bar2','selectedData'),
     Input('inac_bar2', 'selectedData')],
    [State('pass_bar2', 'figure'),
    State('inac_bar2','figure')])
def update_pass_map(club2_name,club1_name,pass2_type,slider2,selectedData,barclickData,inac_click_data,pass_bar,inac_bar):
    pass_player_flag = "n"
    last_week = slider2
    last_match_df = pos_df[(pos_df['gameweek'] == last_week) & (pos_df['teamName'] == club2_name)]
    last_match_df['X'] = 100 - last_match_df['X']
    last_match_df['Y'] = 100 - last_match_df['Y']
    match_id = last_match_df['matchId'].unique()[0]
    team_id = last_match_df['teamId'].unique()[0]
    if (selectedData is None) and (barclickData is None) and (inac_click_data is None):
        if pass2_type == 'All Passes':
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id)]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id)]
        else:
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['subEventName'] == pass2_type)]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id) & (pass_acc['subEventName'] == pass2_type)]
    elif selectedData is not None:
        pass_player_flag = "y"
        points = selectedData['points']
        playerId = []
        matchId = []
        for item in points:
            if 'customdata' in item:
                playerId.append(item['customdata'][0])
                matchId.append(item['customdata'][1])

        if barclickData is not None:
            points = barclickData['points']
            time_categories = []
            player_sender_id = []
            for item in points:
                time_categories.append(item['x'])
                player_sender_id.append(item['customdata'][0])

            if '-' in str(player_sender_id[0]):
                player_sender_id = playerId[:]

            if pass2_type == 'All Passes':
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId)) & (pass_df['timeCat'].isin(time_categories)) & (pass_df['playerId_sender'].isin(player_sender_id))]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId)) & (pass_acc['playerId'].isin(player_sender_id))]
            else:
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId)) & (
                            pass_df['subEventName'] == pass2_type) & (pass_df['timeCat'].isin(time_categories)) & (pass_df['playerId_sender'].isin(player_sender_id))]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId)) & (
                        pass_acc['subEventName'] == pass2_type) & (pass_acc['timeCat'].isin(time_categories)) & (pass_acc['playerId'].isin(player_sender_id))]
        else:
            if pass2_type == 'All Passes':
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId))]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId))]
            else:
                pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['playerId_sender'].isin(playerId)) & (
                            pass_df['subEventName'] == pass2_type)]
                df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['playerId'].isin(playerId)) & (
                        pass_acc['subEventName'] == pass2_type)]
    else:
        points = barclickData['points']
        time_categories = []
        for item in points:
            time_categories.append(item['x'])
        if pass2_type == 'All Passes':
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['timeCat'].isin(time_categories))]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id) & (pass_acc['timeCat'].isin(time_categories))]
        else:
            pass_net = pass_df[(pass_df['matchId'] == match_id) & (pass_df['teamId'] == team_id) & (pass_df['timeCat'].isin(time_categories)) & (
                        pass_df['subEventName'] == pass2_type)]
            df_acc = pass_acc[(pass_acc['matchId'] == match_id) & (pass_acc['teamId'] == team_id) & (pass_acc['timeCat'].isin(time_categories)) & (
                        pass_acc['subEventName'] == pass2_type)]

    pass_net['X_sender'] = 100 - pass_net['X_sender']
    pass_net['Y_sender'] = 100 - pass_net['Y_sender']
    pass_net['X_receiver'] = 100 - pass_net['X_receiver']
    pass_net['Y_receiver'] = 100 - pass_net['Y_receiver']


    opponent_flag = 'y'
    pass_network = create_passing_network_map(last_match_df,pass_net,opponent_flag)
    if barclickData is None:
        pass_bar,ac_df = create_passing_bars(pass_net,pass2_type,pass_player_flag)
        inac_bar, inac_df = create_inaccurate_pass_bars(df_acc, pass2_type, pass_player_flag)

        per_df = ac_df.merge(inac_df).groupby(["matchId","teamId"]).agg({"not accurate":"sum","Pass_count":"sum"}).reset_index()
        per_df["accuracy"] = (per_df["Pass_count"] / (per_df["not accurate"] + per_df['Pass_count'])) * 100
        accuracy = round(per_df["accuracy"].mean(), 2)
    else:
        ac_df = pass_net \
            .groupby(['matchId', 'teamId', 'timeCat']) \
            .agg({'Label': 'count'}) \
            .reset_index().rename(columns={'Label': 'Pass_count'})
        if pass_player_flag == "y":
            ac_df = pass_net \
                .groupby(['matchId', 'teamId', 'timeCat', 'playerId_sender', 'shortName_sender']) \
                .agg({'Label': 'count'}) \
                .reset_index().rename(columns={'Label': 'Pass_count'})
        inac_df = pass_acc \
            .groupby(['matchId', 'teamId', 'timeCat']) \
            .agg({'not accurate': 'sum'}) \
            .reset_index().rename(columns={'Label': 'not accurate'})
        if pass_player_flag == "y":
            inac_df = pass_acc \
                .groupby(['matchId', 'teamId', 'timeCat', 'playerId', 'shortName_sender']) \
                .agg({'not accurate': 'sum'}) \
                .reset_index().rename(columns={'Label': 'not accurate'})
        per_df = ac_df.merge(inac_df).groupby(["matchId","teamId"]).agg({"not accurate":"sum","Pass_count":"sum"}).reset_index()
        per_df["accuracy"] = (per_df["Pass_count"] / (per_df["not accurate"] + per_df['Pass_count'])) * 100
        accuracy = round(per_df["accuracy"].mean(), 2)

    acc_gauge = passacc(accuracy, "passacc2")
    return pass_network,pass_bar,acc_gauge,inac_bar


@app.callback(
    Output('opponent1', 'children'),Output('scorecard1','children'),Output('result1','children'),Output("result1",'style'),
    [Input('club1_header', 'children'),Input('slider1','value')])

def update_match_card(club1_name, slider1):

    week=slider1
    match_df = match_scores[(match_scores['gameweek'] == week) & (match_scores['home_team'] == club1_name)]
    if match_df['result'].values[0] == "Loss":
        color = 'red'
    elif match_df['result'].values[0] == "Win":
        color = 'green'
    else:
        color = 'brown'

    style = {'left-margin': '50%','color': color}

    return match_df['oppostion_team'],match_df['score'],match_df['result'],style


@app.callback(
    Output('opponent2', 'children'),Output('scorecard2','children'),Output('result2','children'),Output("result2",'style'),
    [Input('club2_header', 'children'),Input('slider2','value')])

def update_match_card(club2_name, slider2):

    week=slider2
    match_df = match_scores[(match_scores['gameweek'] == week) & (match_scores['home_team'] == club2_name)]
    if match_df['result'].values[0] == "Loss":
        color = 'red'
    elif match_df['result'].values[0] == "Win":
        color = 'green'
    else:
        color = 'brown'

    style = {'left-margin': '50%','color': color}

    return match_df['oppostion_team'],match_df['score'], match_df['result'],style


if __name__ == '__main__':
    server.run(debug=True)
