import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import traceback

# --- Core Functions ---

def fetch_data(stock_symbol, period="3mo", interval="1d"):
    """Fetches historical stock data."""
    ticker = yf.Ticker(stock_symbol)
    data = ticker.history(period=period, interval=interval)
    return data

def add_indicators(data):
    """Adds technical indicators to the data."""
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
    return data

def create_features_and_labels(data, threshold=0.05):
    """
    Engineers features and labels for predicting today's return based on yesterday's data.
    """
    # The label is based on today's intraday return (Close vs. Open).
    data['Return'] = (data['Close'] - data['Open']) / data['Open']
    data['label'] = (data['Return'] > threshold).astype(int)

    # The features are from the previous day.
    feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'EMA_20']
    data[[f'{col}_prev' for col in feature_cols]] = data[feature_cols].shift(1)

    data.dropna(inplace=True)
    return data

def train_prediction_model(data):
    """
    Trains the classification model on the entire historical dataset.
    """
    features = [col for col in data.columns if col.endswith('_prev')]
    target = 'label'

    X = data[features]
    y = data[target]

    if len(X) < 1:
        return None, None

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y) # Train on the entire dataset for the best prediction
    return model, features

# --- Main App ---

STOCKS = ['CIANAGRO.NS', 'PCBL.NS', 'SJS.NS', 'ACE.NS', 'GRAVITA.NS']
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Stock Analysis Dashboard"),
    dcc.Dropdown(
        id='stock-dropdown',
        options=[{'label': stock, 'value': stock} for stock in STOCKS],
        placeholder="Select a stock",
    ),
    dcc.Graph(id='stock-chart'),
    html.H3(id='prediction-output'),
])

def generate_figure_and_prediction(stock):
    """Generates the chart and prediction for the selected stock."""
    try:
        # 1. Fetch data and add indicators
        raw_data = fetch_data(stock)
        if raw_data.empty:
            return go.Figure().update_layout(title=f"No data for {stock}"), "Could not retrieve data."

        data_with_indicators = add_indicators(raw_data.copy())

        # 2. Create labeled data for training
        training_data = create_features_and_labels(data_with_indicators.copy())

        # 3. Train the model
        if len(training_data) < 5:
            fig = go.Figure(data=[go.Scatter(x=data_with_indicators.index, y=data_with_indicators['Close'], mode='lines', name='Close')])
            fig.update_layout(title=f'Not enough data for {stock} to train model')
            return fig, "Not enough data for prediction."

        model, features = train_prediction_model(training_data)
        if not model:
            fig = go.Figure(data=[go.Scatter(x=data_with_indicators.index, y=data_with_indicators['Close'], mode='lines', name='Close')])
            fig.update_layout(title=f'Failed to train model for {stock}')
            return fig, "Model training failed."

        # 4. Prepare features from the most recent day (yesterday) to predict for today
        latest_data = data_with_indicators.tail(1)
        feature_map = {col: f'{col}_prev' for col in latest_data.columns}
        prediction_input = latest_data.rename(columns=feature_map)

        # 5. Make prediction
        prediction = model.predict(prediction_input[features])
        prediction_text = "Potential 5% return today: YES" if prediction[0] == 1 else "Potential 5% return today: NO"

        # 6. Create figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data_with_indicators.index, y=data_with_indicators['Close'], mode='lines', name='Close'))
        fig.add_trace(go.Scatter(x=data_with_indicators.index, y=data_with_indicators['SMA_20'], mode='lines', name='SMA 20'))
        fig.add_trace(go.Scatter(x=data_with_indicators.index, y=data_with_indicators['EMA_20'], mode='lines', name='EMA 20'))
        fig.update_layout(title=f'{stock} Price Chart')

        return fig, prediction_text
    except Exception as e:
        print(f"Error in generate_figure_and_prediction: {e}")
        traceback.print_exc()
        return go.Figure().update_layout(title=f"An error occurred for {stock}"), "An error occurred during analysis."

@app.callback(
    [Output('stock-chart', 'figure'),
     Output('prediction-output', 'children')],
    [Input('stock-dropdown', 'value')],
    prevent_initial_call=True
)
def update_dashboard(selected_stock):
    """Callback to update the dashboard when a new stock is selected."""
    if not selected_stock:
        return go.Figure(), "Select a stock to see the analysis."

    return generate_figure_and_prediction(selected_stock)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)