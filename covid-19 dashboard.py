import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import glob
import os

folder_path = r"C:\Users\admin\OneDrive\Desktop\certi\sixpharse project\covid"
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

df_list = []
for f in csv_files:
    temp_df = pd.read_csv(f)
    temp_df.columns = temp_df.columns.str.strip().str.lower()
    df_list.append(temp_df)
df = pd.concat(df_list, ignore_index=True)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date', 'confirmed'])

app = dash.Dash(__name__)
available_dates = sorted(df['date'].unique())

app.layout = html.Div([
    html.H1("COVID-19 India Dashboard"),
    html.Div([
        html.Label("Select Date:"),
        dcc.Dropdown(
            id='date-dropdown',
            options=[{'label': d.strftime('%Y-%m-%d'), 'value': d.strftime('%Y-%m-%d')} for d in available_dates],
            value=available_dates[-1].strftime('%Y-%m-%d') if available_dates else None,
            style={'width': '300px'}
        )
    ], style={'marginBottom': 30}),
    dcc.Graph(id='statewise-confirmed'),
    dcc.Graph(id='confirmed-over-time')
])

@app.callback(
    Output('statewise-confirmed', 'figure'),
    Output('confirmed-over-time', 'figure'),
    Input('date-dropdown', 'value')
)
def update_graphs(selected_date):
    if not selected_date:
        return {}, {}

    selected_date_dt = pd.to_datetime(selected_date)

    # Statewise confirmed cases on selected date
    df_selected = df[df['date'] == selected_date_dt]
    if df_selected.empty:
        fig_state = px.bar(title=f"No data for {selected_date}")
    else:
        df_grouped = df_selected.groupby('state/unionterritory')['confirmed'].sum().reset_index()
        fig_state = px.bar(df_grouped.sort_values('confirmed', ascending=False),
                           x='state/unionterritory', y='confirmed',
                           title=f"Statewise Confirmed Cases on {selected_date}",
                           labels={'state/unionterritory': 'State/Union Territory', 'confirmed': 'Confirmed Cases'})

    # Total confirmed cases over time
    df_time = df.groupby('date')['confirmed'].sum().reset_index()
    fig_time = px.line(df_time, x='date', y='confirmed',
                       title='Total Confirmed Cases Over Time in India',
                       labels={'date': 'Date', 'confirmed': 'Confirmed Cases'})

    return fig_state, fig_time

if __name__ == '__main__':
    app.run(debug=True)
