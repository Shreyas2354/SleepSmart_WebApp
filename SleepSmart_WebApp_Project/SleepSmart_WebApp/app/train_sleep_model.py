import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import os

# ✅ Generate synthetic training data
np.random.seed(42)
data = pd.DataFrame({
    'screen_time': np.random.uniform(2, 10, 1000),
    'caffeine': np.random.randint(0, 6, 1000),
    'steps': np.random.randint(1000, 15000, 1000),
    'water': np.random.uniform(0.5, 4, 1000),
    'stress': np.random.randint(1, 10, 1000),
    'device_use': np.random.randint(0, 2, 1000)
})

# ✅ Generate sleep score based on inverse rules
data['sleep_quality'] = 100 \
    - data['screen_time'] * 5 \
    - data['caffeine'] * 3 \
    + data['steps'] / 100 \
    + data['water'] * 5 \
    - data['stress'] * 4 \
    - data['device_use'] * 5

# Clip between 0 and 100
data['sleep_quality'] = data['sleep_quality'].clip(0, 100)

# ✅ Train/Test split
X = data.drop('sleep_quality', axis=1)
y = data['sleep_quality']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ✅ Evaluate
preds = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, preds))
print(f"RMSE: {rmse:.2f}")

# ✅ Save model
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/sleep_model.pkl")
print("Model saved to model/sleep_model.pkl")
