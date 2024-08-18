#
import json
import datetime

#
import pandas

import plotly.graph_objects as go

import flask

import dash
import dash_daq as daq
import dash_table as dt
from dash_table.Format import Format, Scheme, Group, Symbol
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#


#
read_base = ''

color_map = {'red': '#E84A5F', 'yellow': '#FECEA8', 'green': '#99B898'}
status_map = {'red': '🥴', 'yellow': '😑', 'green': '😎'}

data = pandas.read_csv(read_base + 'data.csv', index_col=0)
targets = [x for x in data.columns.values if '_Close' not in x]

with open(read_base + 'co.json', 'r') as f:
    co = json.load(f)

reported_table = pandas.DataFrame(data=[['target metric', 'smape', co[targets[0]]['target_smape'], status_map[co[targets[0]]['target_smape_flag']]],
                                        ['errors behavior', 'normal distribution', co[targets[0]]['errors_normal'], status_map[co[targets[0]]['errors_normal_flag']]],
                                        ['errors behavior', 'autocorrelation', co[targets[0]]['errors_autocorrelated'], status_map[co[targets[0]]['errors_autocorrelated_flag']]],
                                        ['errors behavior', 'stationarity', co[targets[0]]['errors_stationary'], status_map[co[targets[0]]['errors_stationary_flag']]],
                                        ['errors behavior', 'homoscedasticity', co[targets[0]]['errors_homoscedastic'], status_map[co[targets[0]]['errors_homoscedastic_flag']]],
                                        ['errors behavior', 'zero mean', co[targets[0]]['errors_zeromean'], status_map[co[targets[0]]['errors_zeromean_flag']]]],
                                  columns=['Category', 'Measure', 'Value', 'Status'])
reported_table['Value'] = reported_table['Value'].round(decimals=4)

cols_format = [{"name": i, "id": i} for i in reported_table.columns]
cols_format[1]["format"] = Format(
                scheme=Scheme.fixed,
                precision=2,
                group=Group.yes,
                groups=3,
                group_delimiter='.',
                decimal_delimiter=',',
                symbol=Symbol.yes,
                symbol_prefix=u'€')

# server = flask.Flask(__name__)
# app = dash.Dash(__name__, server=server)
dash_app = dash.Dash()
app = dash_app.server


dash_app.layout = html.Div(children=[
    html.H1(children='Last 96 days model performance', style={'textAlign': 'center'}),

    html.Div([

            dcc.Dropdown(id='sns',
                         options=[{'label': i, 'value': i} for i in targets],
                         value=targets[0],
                         multi=False,
                         style={'width': '69%'}
                         ),
            dcc.Graph(id='quotes', style={'width': '100%'}),
html.H2(children='Overall Flags', style={'textAlign': 'center'}),
        html.Div([
            daq.Indicator(
                id='target',
                label="Forecast Precision",
                color="#551A8B",
                value=True,
                size=30
            ),
            daq.Indicator(
                id='errors',
                label="Errors behavior",
                color="#551A8B",
                value=True,
                size=30
            ),
            daq.Indicator(
                id='warns',
                label="X-matrix Warn Signs",
                color="#551A8B",
                value=True,
                size=30
            )]),
html.H2(children='Stats', style={'textAlign': 'center'}),
            dt.DataTable(id='table',
                         columns=cols_format,
                         data=reported_table.to_dict('records')
                         )
        ])
    ])


@dash_app.callback([dash.dependencies.Output('quotes', 'figure'), dash.dependencies.Output('target', 'color'),
                    dash.dependencies.Output('errors', 'color'), dash.dependencies.Output('warns', 'color'),
                    dash.dependencies.Output('table', 'data')],
                   [dash.dependencies.Input('sns', 'value')])
def update_output(series_names):
    if not isinstance(series_names, list):
        series_names = [series_names]

    data = pandas.read_csv(read_base + 'data.csv', index_col=0)
    targets = [x for x in data.columns.values if '_Close' not in x]

    with open(read_base + 'co.json', 'r') as f:
        co = json.load(f)

    series_names = series_names + [x + '_Close' for x in series_names]
    target_series = data.loc[:, series_names]

    fig_quotes = go.Figure()
    tin = [x for x in targets if x in series_names]
    for target in tin:
        fig_quotes.add_trace(
            go.Scatter(x=target_series.index.values, y=target_series[target], visible=True, name=(target + '__Forecasts')))
        fig_quotes.add_trace(
            go.Scatter(x=target_series.index.values, y=target_series[target + '_Close'], visible=True, name=(target + '__Real')))

    reported_table = pandas.DataFrame(data=[['target metric', 'smape', co[tin[0]]['target_smape'], status_map[co[tin[0]]['target_smape_flag']]],
                                            ['errors behavior', 'normal distribution', co[tin[0]]['errors_normal'], status_map[co[tin[0]]['errors_normal_flag']]],
                                            ['errors behavior', 'autocorrelation', co[tin[0]]['errors_autocorrelated'], status_map[co[tin[0]]['errors_autocorrelated_flag']]],
                                            ['errors behavior', 'stationarity', co[tin[0]]['errors_stationary'], status_map[co[tin[0]]['errors_stationary_flag']]],
                                            ['errors behavior', 'homoscedasticity', co[tin[0]]['errors_homoscedastic'], status_map[co[tin[0]]['errors_homoscedastic_flag']]],
                                            ['errors behavior', 'zero mean', co[tin[0]]['errors_zeromean'], status_map[co[tin[0]]['errors_zeromean_flag']]]],
                                      columns=['Category', 'Measure', 'Value', 'Status'])

    reported_table['Value'] = reported_table['Value'].round(decimals=4)

    return fig_quotes, color_map[co[tin[0]]['target']], color_map[co[tin[0]]['errors']], color_map[
        co[tin[0]]['warns']], reported_table.to_dict('records')

dash_app.run_server(debug=True, use_reloader=False)
