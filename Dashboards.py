import dash
from dash import html, dcc, Input, Output, dash_table
import pandas as pd
import plotly.express as px

# Load datasets
pitch_df = pd.read_csv(
    "https://drive.google.com/uc?export=download&id=1LPYqxqRuIcUxHldalhwEtCaWl2zr1aHc",
    low_memory=False,
    on_bad_lines='skip'  # Skip malformed rows
)
batting_df = pd.read_csv("necbl_combined_batting_stats.csv", low_memory=False)

# Initialize app
app = dash.Dash(__name__)
app.title = "NECBL 2024 Dashboard"

# Layout
app.layout = html.Div([
    html.H1("NECBL 2024 Dashboard", style={'textAlign': 'center'}),
    dcc.Tabs(id='tabs', value='pitch', children=[
        dcc.Tab(label='Pitching Dashboard', value='pitch'),
        dcc.Tab(label='Batting Percentiles', value='batting'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_tab(tab):
    if tab == 'pitch':
        return html.Div([
            html.Label("Select Pitcher:"),
            dcc.Dropdown(
                id='pitcher-dropdown',
                options=[{'label': name, 'value': name} for name in sorted(pitch_df['Pitcher'].dropna().unique())],
                value=None,
                placeholder="Select a pitcher",
                style={'width': '50%'}
            ),
            html.Div(id='pitch-summary-table'),
            dcc.Graph(id='break-scatterplot')
        ])
    elif tab == 'batting':
        return html.Div([
            html.H3("Player Percentile Rankings"),

            html.Div([
                html.Label("Minimum PA:"),
                dcc.Input(
                    id='min-pa-input',
                    type='number',
                    value=0,
                    min=0,
                    debounce=True,
                    style={'marginBottom': '10px'}
                )
            ]),

            html.Div([
                html.Label("Filter by Team:"),
                dcc.Dropdown(
                    id='team-dropdown',
                    options=[{'label': t, 'value': t} for t in sorted(batting_df['Team'].dropna().unique())],
                    placeholder="All Teams",
                    value=None,
                    style={'width': '50%', 'marginBottom': '10px'}
                )
            ]),

            dash_table.DataTable(
                id='batting-table',
                columns=[
                    {"name": "Player", "id": "Player"},
                    {"name": "Team", "id": "Team"},
                    {"name": "PA", "id": "PA"},
                    {"name": "wOBA", "id": "wOBA", "type": "numeric"},
                    {"name": "wOBA_Pctl", "id": "wOBA_Pctl", "type": "numeric"},
                    {"name": "OBP_Pctl", "id": "OBP_Pctl", "type": "numeric"},
                    {"name": "SLG_Pctl", "id": "SLG_Pctl", "type": "numeric"},
                    {"name": "OPS_Pctl", "id": "OPS_Pctl", "type": "numeric"},
                ],
                sort_action="native",
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
                style_cell={'textAlign': 'center'},
                style_data_conditional=[]
            )
        ])

@app.callback(
    [Output('pitch-summary-table', 'children'),
     Output('break-scatterplot', 'figure')],
    Input('pitcher-dropdown', 'value')
)
def update_pitching_tab(selected_pitcher):
    filtered_df = pitch_df[pitch_df['Pitcher'] == selected_pitcher] if selected_pitcher else pitch_df

    summary = (
        filtered_df.groupby('AutoPitchType')
        .agg(
            Usage=('AutoPitchType', 'count'),
            AvgVelocity=('RelSpeed', 'mean'),
            AvgSpinRate=('SpinRate', 'mean'),
            AvgIVB=('InducedVertBreak', 'mean'),
            AvgHB=('HorzBreak', 'mean')
        )
        .reset_index()
    )

    total_pitches = summary['Usage'].sum()
    summary['UsagePct'] = (summary['Usage'] / total_pitches * 100).round(1)
    summary = summary[['AutoPitchType', 'UsagePct', 'AvgVelocity', 'AvgSpinRate', 'AvgIVB', 'AvgHB']].round(2)

    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in summary.columns],
        data=summary.to_dict("records"),
        style_table={'overflowX': 'auto', 'padding': '10px'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center'}
    )

    scatter = px.scatter(
        filtered_df,
        x="HorzBreak",
        y="InducedVertBreak",
        color="AutoPitchType",
        title=f"Horizontal vs Vertical Break - {selected_pitcher or 'All Pitchers'}",
        labels={"HorzBreak": "Horizontal Break", "InducedVertBreak": "Vertical Break"},
    )

    scatter.update_layout(
        xaxis=dict(range=[-25, 25]),
        yaxis=dict(range=[-25, 25]),
        height=600
    )

    return table, scatter

@app.callback(
    [Output("batting-table", "data"),
     Output("batting-table", "style_data_conditional")],
    [Input("min-pa-input", "value"),
     Input("team-dropdown", "value")]
)
def update_batting_table(min_pa, team):
    filtered = batting_df.copy()

    if team:
        filtered = filtered[filtered["Team"] == team]

    filtered = filtered[filtered["PA"] >= (min_pa or 0)]

    if filtered.empty:
        return [], []

    # Recalculate percentiles
    filtered['OBP_Pctl'] = filtered['OBP'].rank(pct=True) * 100
    filtered['SLG_Pctl'] = filtered['SLG'].rank(pct=True) * 100
    filtered['OPS_Pctl'] = filtered['OPS'].rank(pct=True) * 100
    filtered['wOBA_Pctl'] = filtered['wOBA'].rank(pct=True) * 100

    filtered = filtered.round({
        'wOBA': 3,
        'wOBA_Pctl': 1,
        'OBP_Pctl': 1,
        'SLG_Pctl': 1,
        'OPS_Pctl': 1
    })

    # Gradient styling
    style_conditional = []
    for col in ['wOBA_Pctl', 'OBP_Pctl', 'SLG_Pctl', 'OPS_Pctl']:
        for pct in range(0, 101, 10):
            red = int(255 * (pct / 100))
            blue = int(255 * (1 - pct / 100))
            style_conditional.append({
                'if': {'column_id': col, 'filter_query': f'{{{col}}} >= {pct}'},
                'backgroundColor': f'rgba({red}, 0, {blue}, 0.9)',
                'color': 'white'
            })

    return filtered.to_dict("records"), style_conditional


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

