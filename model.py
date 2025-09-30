from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def train_model(data):
    """
    Trains a RandomForestClassifier model.
    """
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'EMA_20']
    target = 'label'

    X = data[features]
    y = data[target]

    # Split data, but for time series, we should not shuffle
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model, features

def predict(model, data, features):
    """
    Makes a prediction using the trained model.
    """
    return model.predict(data[features])