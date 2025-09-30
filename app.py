import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from data_fetcher import fetch_data
from feature_engineering import add_indicators, create_labels
from model import train_model, predict

# Stock list
STOCKS = ['CIANAGRO.NS', 'PCBL.NS', 'SJS.NS', 'ACE.NS', 'GRAVITA.NS']
# Correcting stock symbols for yfinance
# CIANAGRO -> CIANAGRO.NS (CIE Automotive India Ltd)
# PCBL -> PCBL.NS (PCBL Ltd)
# SJS -> SJS.NS (SJS Enterprises Ltd)
# ACE -> ACE.NS (Action Construction Equipment Ltd)
# GRAVITA -> GRAVITA.NS (Gravita India Ltd)


# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Stock Analysis Dashboard"),
    dcc.Dropdown(
        id='stock-dropdown',
        options=[{'label': stock, 'value': stock} for stock in STOCKS],
        value=STOCKS[0]
    ),
    dcc.Graph(id='stock-chart'),
    html.H3(id='prediction-output'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds (update every minute)
        n_intervals=0
    )
])

@app.callback(
    [Output('stock-chart', 'figure'),
     Output('prediction-output', 'children')],
    [Input('stock-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard(selected_stock, n):
    # Fetch data
    data = fetch_data(selected_stock)

    # Feature Engineering
    data = add_indicators(data)

    # Create labels for model training (excluding the last row for prediction)
    data_with_labels = create_labels(data.copy())

    # Train model
    model, features = train_model(data_with_labels)

    # Predict
    prediction = predict(model, data.tail(1), features)
    prediction_text = "Potential 5% return today: YES" if prediction[0] == 1 else "Potential 5% return today: NO"

    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], mode='lines', name='SMA 20'))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_20'], mode='lines', name='EMA 20'))
    fig.update_layout(title=f'{selected_stock} Price Chart',
                      xaxis_title='Date',
                      yaxis_title='Price')

    return fig, prediction_text

if __name__ == '__main__':
    app.run_server(debug=True)