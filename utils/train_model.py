import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)
    
    # Features: Temperature, Humidity, Wind Speed, Rainfall, NDVI, Historical Fire
    temperature = np.random.uniform(15, 45, num_samples)
    humidity = np.random.uniform(10, 80, num_samples)
    wind_speed = np.random.uniform(0, 40, num_samples)
    rainfall = np.random.uniform(0, 50, num_samples)
    ndvi = np.random.uniform(0.1, 0.9, num_samples)
    historical_fire = np.random.randint(0, 2, num_samples)
    
    data = pd.DataFrame({
        'temperature': temperature,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'rainfall': rainfall,
        'ndvi': ndvi,
        'historical_fire': historical_fire
    })
    
    # Define risk based on some heuristic logic
    # Higher risk: High temp, Low humidity, High wind, Low rainfall, High NDVI (more fuel), Historical fire
    def calculate_risk(row):
        score = (row['temperature'] * 0.4) - (row['humidity'] * 0.3) + (row['wind_speed'] * 0.2) - (row['rainfall'] * 0.3) + (row['ndvi'] * 10) + (row['historical_fire'] * 10)
        
        if score > 25:
            return 2 # High Risk
        elif score > 15:
            return 1 # Medium Risk
        else:
            return 0 # Low Risk

    data['risk'] = data.apply(calculate_risk, axis=1)
    return data

def train_model():
    print("Generating synthetic data...")
    data = generate_synthetic_data(2000)
    
    # Save a copy of the data
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data.to_csv(os.path.join(data_dir, 'satellite_data.csv'), index=False)
    print(f"Data saved to {os.path.join(data_dir, 'satellite_data.csv')}")
    
    X = data.drop('risk', axis=1)
    y = data['risk']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    model_dir = os.path.join(os.getcwd(), 'model')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    joblib.dump(model, os.path.join(model_dir, 'wildfire_model.pkl'))
    print(f"Model saved to {os.path.join(model_dir, 'wildfire_model.pkl')}")

if __name__ == "__main__":
    train_model()
