import pandas as pd
import numpy as np

def preprocess_input(data):
    """
    Preprocesses the raw data for model prediction.
    Ensures correct feature alignment.
    """
    # Features: temperature, humidity, wind_speed, rainfall, ndvi, historical_fire
    features = ['temperature', 'humidity', 'wind_speed', 'rainfall', 'ndvi', 'historical_fire']
    
    df = pd.DataFrame([data])
    
    # Fill missing values if any
    for feature in features:
        if feature not in df.columns:
            df[feature] = 0
            
    return df[features]
