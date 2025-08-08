# train_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# Create synthetic dataset
np.random.seed(42)
data = pd.DataFrame({
    'screen_time': np.random.uniform(2, 10, 1000),
    'caffeine': np.random.randint(0, 6, 1000),
    'steps': np.random.randint(1000, 15000, 1000),
    'water': np.random.uniform(0.5, 4, 1000),
    'stress': np.random.randint(1, 10, 1000),
    'device_use': np.random.randint(0, 2, 1000)
})
data['sleep_quality'] = 100 \
    - data['screen_time'] * 5 \
    - data['caffeine'] * 3 \
    + data['steps'] / 100 \
    + data['water'] * 5 \
    - data['stress'] * 4 \
    - data['device_use'] * 5
data['sleep_quality'] = data['sleep_quality'].clip(0, 100)

X = data.drop('sleep_quality', axis=1)
y = data['sleep_quality']

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save to correct path
model_dir = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "sleep_model.pkl")
joblib.dump(model, model_path)

print(f"✅ Model trained and saved to: {model_path}")
