import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

# Read the CSV file

df = pd.read_csv('vdot_crash_data.csv')



# Strip any extra spaces from column names
df.columns = df.columns.str.strip()

# Create the Dash app
app = dash.Dash(__name__)

# Layout for the dashboard
app.layout = html.Div([
    html.H1("VDOT Crash Data Dashboard", style={'text-align': 'center', 'font-size': '36px', 'margin-bottom': '10px'}),
    html.P(
        "This dashboard provides insights into crashes in Virginia, filtered by area type, cities/counties, weather-related conditions, lighting conditions, and more. It includes a crash heatmap and highlights cities with the most crashes. You can select the year and city from the dropdowns.",
        style={'text-align': 'center', 'font-size': '20px', 'margin-bottom': '30px', 'line-height': '1.5'}
    ),

    # Total, Urban, and Rural Crashes in Virginia by Year
    html.Div([dcc.Graph(id='total-crashes-by-year')], style={'width': '100%', 'display': 'inline-block', 'margin-bottom': '30px'}),

    # Dropdowns with header text
    html.Div([
        html.P("Select cities, year, and area type:", style={'text-align': 'center', 'font-size': '30px', 'margin-bottom': '10px'}),
        html.Div([
            html.Label("Select Year ▼", style={'font-size': '22px', 'font-weight': 'bold'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(df['Crash Year'].unique())],
                value=sorted(df['Crash Year'].unique())[0],
                style={'width': '30%', 'display': 'inline-block', 'font-size': '20px', 'margin-right': '2%', 'padding': '10px'}
            ),
            html.Label("Select City ▼", style={'font-size': '22px', 'font-weight': 'bold'}),
            dcc.Dropdown(
                id='city-dropdown',
                options=[{'label': city, 'value': city} for city in sorted(df['Physical Juris Name'].unique())],
                value=sorted(df['Physical Juris Name'].unique())[0],
                style={'width': '30%', 'display': 'inline-block', 'font-size': '20px', 'margin-right': '2%', 'padding': '10px'}
            ),
            html.Label("Select Area Type ▼", style={'font-size': '22px', 'font-weight': 'bold'}),
            dcc.Dropdown(
                id='area-dropdown',
                options=[{'label': area, 'value': area} for area in sorted(df['Area Type'].unique())],
                value='Urban',
                style={'width': '30%', 'display': 'inline-block', 'font-size': '20px', 'padding': '10px'}
            ),
        ], style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '30px'}),
    ]),

    # Urban and Rural Crashes per Year in Selected City
    html.Div([dcc.Graph(id='urban-rural-crashes-city')], style={'width': '100%', 'display': 'inline-block', 'margin-bottom': '30px'}),

    # Crashes by Weather Condition and Lighting Condition
    html.Div([
        html.Div([dcc.Graph(id='crashes-by-weather')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='crashes-by-lighting')], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'margin-bottom': '30px'}),

    # Map Visualization (Urban Crash Hotspots)
    html.Div([dcc.Graph(id='urban-crash-hotspots')], style={'width': '100%', 'display': 'inline-block', 'margin-bottom': '30px'}),

    # Top 10 Cities/Counties with Highest Number of Crashes
    html.Div([dcc.Graph(id='urban-safety-index')], style={'width': '100%', 'display': 'inline-block'})
])

# Callback to update 'Total Crashes by Year in Virginia'
@app.callback(
    Output('total-crashes-by-year', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_total_crashes_by_year(_):
    total_crashes = df.groupby('Crash Year').size()
    urban_crashes = df[df['Area Type'] == 'Urban'].groupby('Crash Year').size()
    rural_crashes = df[df['Area Type'] == 'Rural'].groupby('Crash Year').size()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=total_crashes.index.astype(int), y=total_crashes.values, mode='lines+markers', name='Total Crashes'))
    fig.add_trace(go.Scatter(x=urban_crashes.index.astype(int), y=urban_crashes.values, mode='lines+markers', name='Urban Crashes', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=rural_crashes.index.astype(int), y=rural_crashes.values, mode='lines+markers', name='Rural Crashes', line=dict(dash='dot')))
    fig.update_layout(title='<b>Total, Urban, and Rural Crashes in Virginia by Year</b>', xaxis_title='Year', yaxis_title='Number of Crashes', font={'size': 16})
    return fig

# Callback to update 'Urban and Rural Crashes in Selected City'
@app.callback(
    Output('urban-rural-crashes-city', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_urban_rural_crashes_city(selected_city):
    filtered_data = df[df['Physical Juris Name'] == selected_city]
    urban_crashes = filtered_data[filtered_data['Area Type'] == 'Urban'].groupby('Crash Year').size()
    rural_crashes = filtered_data[filtered_data['Area Type'] == 'Rural'].groupby('Crash Year').size()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=urban_crashes.index.astype(int), y=urban_crashes.values, mode='lines+markers', name='Urban Crashes'))
    fig.add_trace(go.Scatter(x=rural_crashes.index.astype(int), y=rural_crashes.values, mode='lines+markers', name='Rural Crashes', line=dict(dash='dash')))
    fig.update_layout(
        title=f'<b>Urban and Rural Crashes in {selected_city} by Year</b>',
        xaxis_title='Year',
        yaxis_title='Number of Crashes',
        font={'size': 16}
    )
    return fig

# Callback to update 'Crashes by Weather Condition'
@app.callback(
    Output('crashes-by-weather', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('city-dropdown', 'value'),
     Input('area-dropdown', 'value')]
)
def update_crashes_by_weather(selected_year, selected_city, selected_area):
    filtered_data = df[(df['Crash Year'] == selected_year) & (df['Physical Juris Name'] == selected_city) & (df['Area Type'] == selected_area)]
    weather_crashes = filtered_data.groupby('Weather Condition').size().sort_values(ascending=False)

    fig = px.pie(names=weather_crashes.index, values=weather_crashes.values, title=f"<b>Crashes by Weather Condition in {selected_city} ({selected_year})</b>")
    fig.update_layout(font={'size': 16})
    return fig

# Callback to update 'Crashes by Lighting Condition'
@app.callback(
    Output('crashes-by-lighting', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('city-dropdown', 'value'),
     Input('area-dropdown', 'value')]
)
def update_crashes_by_lighting(selected_year, selected_city, selected_area):
    filtered_data = df[(df['Crash Year'] == selected_year) & (df['Physical Juris Name'] == selected_city) & (df['Area Type'] == selected_area)]
    lighting_crashes = filtered_data.groupby('Light Condition').size().sort_values(ascending=False)

    fig = px.bar(
        x=lighting_crashes.index,
        y=lighting_crashes.values,
        labels={'x': 'Lighting Condition', 'y': 'Number of Crashes'},
        title=f"<b>Crashes by Lighting Condition in {selected_city} ({selected_year})</b>"
    )
    fig.update_layout(font={'size': 16})
    return fig

# Callback to update 'Urban Crash Hotspots'
@app.callback(
    Output('urban-crash-hotspots', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('city-dropdown', 'value'),
     Input('area-dropdown', 'value')]
)
def update_urban_crash_hotspots(selected_year, selected_city, selected_area):
    filtered_data = df[(df['Crash Year'] == selected_year) & (df['Physical Juris Name'] == selected_city) & (df['Area Type'] == selected_area)]
    hotspots = filtered_data.groupby(['x', 'y']).size().reset_index(name='Crash Count')

    fig = px.density_mapbox(
        hotspots, lat="y", lon="x", z="Crash Count", radius=10, mapbox_style="carto-positron",
        title=f'<b>Crash Hotspots in {selected_city} ({selected_area})</b>', zoom=10,
        center={"lat": hotspots["y"].mean(), "lon": hotspots["x"].mean()}
    )
    fig.update_layout(font={'size': 16})
    return fig

# Callback to update 'Top 10 Cities/Counties with Highest Number of Crashes'
@app.callback(
    Output('urban-safety-index', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('area-dropdown', 'value')]
)
def update_urban_safety_index(selected_year, selected_area):
    filtered_data = df[(df['Crash Year'] == selected_year) & (df['Area Type'] == selected_area)]
    top_cities = filtered_data.groupby('Physical Juris Name').size().sort_values(ascending=False).head(10)

    fig = px.bar(
        x=top_cities.values, y=top_cities.index, orientation='h',
        labels={'x': 'Crash Count', 'y': 'City/County'},
        title=f'<b>Top 10 Cities/Counties with Highest Crash Count ({selected_area}, {selected_year})</b>'
    )
    fig.update_layout(font={'size': 16})
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
