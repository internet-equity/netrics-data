import pandas as pd
from datetime import date

import warnings
from dash import dash_table

import plotly.express as px
warnings.filterwarnings('ignore')

df = pd.read_csv('grouped.csv')
df.drop(columns = 'Unnamed: 0', inplace = True)
df.rename(columns={"anomaly": "Point Anomalies", "date_missing_entries":"Missing Points"}, inplace=True)

# Import and merge Change Point Calculation
cp = pd.read_csv('change_points.csv')
cp.rename(columns={"Date": "date", "Change_Pts_per_day": "Collective Anomalies"}, inplace=True)

final_df = df.merge(cp, how = 'left', on = ['date', 'deviceID', 'target'] )
final_df['Point Anomalies'] = pd.to_numeric(final_df['Point Anomalies'], errors='coerce')
final_df['Missing Points'] = pd.to_numeric(final_df['Missing Points'], errors='coerce')

# Values for the series
values = [
    "nm-mngd-20210518-221fcce5",
    "nm-mngd-20210518-f2242dfd",
    "nm-mngd-20210924-77f105f0",
    "nm-mngd-20210927-1aaa32b5",
    "nm-mngd-20210927-4a1de38c",
    "nm-mngd-20210927-9044c591",
    "nm-mngd-20220218-bcc572f4",
    "nm-mngd-20220506-98c85a91",
    "nm-mngd-20220505-7db0ce31",
    "nm-mngd-20220505-23cccfed"
]

# Creating the series with label "deviceID"
deviceID_series = pd.Series(values, name="deviceID")

# Neighborhood values
neighborhood_values = [
    "Hyde Park - South Side",
    "Hyde Park - South Side",
    "Bridgeport - South Side",
    "Albany Park - North Side",
    "Avondale - North Side",
    "River Forest - Suburbs",
    "Avondale - North Side",
    "South Shore - South Side",
    "Logan Square - North Side",
    "Logan Square - North Side"
]

# Convert the series into a DataFrame and add the Neighborhood column
deviceID_df = deviceID_series.to_frame()
deviceID_df["Location"] = neighborhood_values

# Splitting the 'Neighborhood' column into two new columns
deviceID_df[['Neighborhood', 'Region']] = deviceID_df['Location'].str.split(' - ', expand=True)

# Dropping the original 'Neighborhood' column
deviceID_df = deviceID_df.drop(columns='Location')

final_df = final_df.merge(deviceID_df, how = 'left', on = ['deviceID'] )

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Initialize the Dash app and include Bootstrap CSS and JS
app = dash.Dash(__name__,
                external_stylesheets=['https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css'],
                external_scripts=['https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js'])


@app.callback(Output('literature-review', 'href'), [Input('dummy', 'children')])
def update_literature_review_link(children):
    pdf_path = 'path_to_your_pdf_file.pdf'
    return pdf_path

app.layout = html.Div([
    # Navbar for small screens
    html.Nav([
        html.Div(className="container-fluid", children=[
            html.Div(className="navbar-header", children=[
                html.Button(className="navbar-toggle", type="button", **{
                    'data-toggle': 'collapse', 'data-target': '#myNavbar'
                }, children=[
                    html.Span(className="icon-bar"),
                    html.Span(className="icon-bar"),
                    html.Span(className="icon-bar")
                ]),
                html.A(className="navbar-brand", href="#", children="Logo")
            ]),
            html.Div(id="myNavbar", className="collapse navbar-collapse", children=[
                html.Ul(className="nav navbar-nav", children=[
                    html.Li(className="active", children=[
                        dcc.Link('Dashboard', href="#section1", className="nav-link")
                    ]),
                    html.Li(children=[
                        dcc.Link('About', href="#section2", className="nav-link")
                    ]),
                    html.Li(children=[
                        dcc.Link('Literature Review', href="", className="nav-link", target="_blank",
                                 id='literature-review')
                    ])
                ])
            ])
        ])
    ], className="navbar navbar-inverse visible-xs"),

    # Main container
    html.Div(className="container-fluid", children=[
        html.Div(className="row content", children=[
            # Sidebar
            html.Div(className="col-sm-3 sidenav hidden-xs", children=[
                html.H2(children="Internet Equity Dashboard"),
                html.Ul(className="nav nav-pills nav-stacked", children=[
                    html.Li(className="active", children=[
                        dcc.Link('Dashboard', href="#section1", className="nav-link")
                    ]),
                    html.Li(children=[
                        dcc.Link('About', href="#section2", className="nav-link")
                    ]),
                    html.Li(children=[
                        dcc.Link('Literature Review', href="", className="nav-link", target="_blank",
                                 id='literature-review-link')
                    ])
                ])
            ]),

            # Content section
            html.Div(className="col-sm-9", children=[
                # Section 1 - Dashboard content
                html.Div(id="section1", children=[
                    html.H1('DASHBOARD'),
                    dcc.Dropdown(
                    id='target-dropdown',
                    options=[{'label': target, 'value': target} for target in final_df['target'].unique()] + \
                    [{'label': 'All', 'value': 'All'}],
                    value=final_df['target'].unique()[0],
                    clearable=False
                    ),
                    dcc.Dropdown(
                    id='region-dropdown',
                    options=[{'label': region, 'value': region} for region in final_df['Region'].unique()] + \
                    [{'label': 'All', 'value': 'All'}],
                    value=final_df['Region'].unique()[0],
                    clearable=False
                    ),
                    dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(2022, 1, 1),
                    max_date_allowed=date(2022, 12, 31),
                    initial_visible_month=date(2022, 12, 1),
                    end_date=date(2022, 12, 31)
                    ),
                    html.Div(id='table-container'),
                    dcc.Graph(id='bar-graph'),
                    dcc.Graph(id='bar2')
                ]),

                # Section 2 - About content
                html.Div(id="section2", children=[
                    html.H1('About Our Project'),
                    html.P('This is a brief description of our project.'),
                    html.P('You can type out whatever text you need for the "About" section.'),
                    html.P('Add more paragraphs or content as needed.')
                ]),
                html.Div(id='dummy', style={'display': 'none'})
            ])
        ])
    ])
])

# Define callback to update table
@app.callback(
    Output('table-container', 'children'),
    [Input('target-dropdown', 'value'),
     Input('region-dropdown', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')]
)
def update_table(selected_target, selected_region, start_date, end_date):
    # The rest of your data processing and table update logic
    if selected_region == 'All':
        if selected_target == 'All':
            filtered_df = final_df[((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
        else:
            filtered_df = final_df[(final_df['target'] == selected_target) & \
                           ((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
    else:
        if selected_target == 'All':
            filtered_df = final_df[(final_df['Region'] == selected_region) &\
                           ((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
        else:
            filtered_df = final_df[(final_df['target'] == selected_target) & (final_df['Region'] == selected_region) &\
                           ((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
    
    
    filtered_grouped = filtered_df.groupby(['deviceID','Neighborhood','Region','target'])[['Point Anomalies',
                                                         'Collective Anomalies',
                                                         'Missing Points']].mean().reset_index()
    
    # Only display 'date' 'anomaly' and 'date_missing_entries' columns
    # Also rounding the results to 2 decimals
    columns_to_display = ['deviceID', 'Point Anomalies','Collective Anomalies',
                          'Missing Points','Neighborhood','Region','target']
    filtered_grouped = filtered_grouped[columns_to_display].round(2)
    
    # Aggregate
    aggregate_row = {
        'deviceID': 'Mean',
        'Point Anomalies': filtered_grouped['Point Anomalies'].mean(),
        'Collective Anomalies': filtered_grouped['Collective Anomalies'].mean(),
        'Missing Points': filtered_grouped['Missing Points'].mean()
    }
    filtered_grouped = pd.concat([filtered_grouped,pd.DataFrame([aggregate_row])], ignore_index=True).round(2)

    return dash_table.DataTable(
        data=filtered_grouped.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in columns_to_display],
        style_table={'width': '100%'},  # Use 100% of the container width
        style_cell={
            'textAlign': 'center',  # Center cell content
            'width': '{}%'.format(100 / len(columns_to_display)),  # Equal column widths
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        }
    )

# Define callback to update graphs
@app.callback(
    [Output('bar-graph', 'figure'),
     Output('bar2', 'figure')],
    [Input('target-dropdown', 'value'),
     Input('region-dropdown', 'value'),
     Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')]
)

def update_plot(selected_target, selected_region, start_date, end_date):
    
    if selected_region == 'All':
        if selected_target == 'All':
            filtered_df = final_df[((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
        else:
            filtered_df = final_df[(final_df['target'] == selected_target) & \
                           ((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
    else:
        if selected_target == 'All':
            filtered_df = final_df[(final_df['Region'] == selected_region) &\
                           ((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
        else:
            filtered_df = final_df[(final_df['target'] == selected_target) & (final_df['Region'] == selected_region) &\
                           ((final_df['date'] > start_date) & (final_df['date'] <= end_date))]
    
    
    
    filtered_grouped = filtered_df.groupby(['deviceID','Neighborhood','Region','target'])[['Point Anomalies',
                                                         'Collective Anomalies',
                                                         'Missing Points']].mean().reset_index()
    
    # Only display 'date' 'anomaly' and 'date_missing_entries' columns
    # Also rounding the results to 2 decimals
    columns_to_display = ['deviceID', 'Point Anomalies','Collective Anomalies',
                          'Missing Points','Neighborhood','Region','target']
    filtered_grouped = filtered_grouped[columns_to_display].round(2)
    
    # Aggregate
    aggregate_row = {
        'deviceID': 'Mean',
        'Point Anomalies': filtered_grouped['Point Anomalies'].mean(),
        'Collective Anomalies': filtered_grouped['Collective Anomalies'].mean(),
        'Missing Points': filtered_grouped['Missing Points'].mean()
    }
    
    filtered_grouped = pd.concat([filtered_grouped,pd.DataFrame([aggregate_row])], ignore_index=True).round(2)
    
    fig1 = px.bar(filtered_grouped, x='Region', y=['Point Anomalies', 'Collective Anomalies', 'Missing Points'],
                  title='average anomalies by region')
    fig2 = px.bar(filtered_grouped, x='target', y=['Point Anomalies', 'Collective Anomalies', 'Missing Points'],
                  title='average anomalies by target')

    return fig1, fig2


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
