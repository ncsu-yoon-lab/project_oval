import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Load the dataset
data = pd.read_csv("C:\Users\malin\Documents\GitHub\project-oval\Data\data_gps_logger_test4.csv")

# Convert the degrees minutes to decimal degrees
def convert_degrees(point):
    degrees = np.floor(point / 100)
    minutes = point - degrees * 100
    return degrees + minutes / 60

data['gps_lat'] = data['gps_lat'].apply(convert_degrees)
data['gps_lon'] = data['gps_lon'].apply(lambda x: -convert_degrees(x))

# Prepare the features (input data) and labels (correct points)
X = data[['gps_lat', 'gps_lon']].values
y = data[['latitude', 'longitude']].values

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Function to adjust slightly off points
def adjust_lat_lon(off_lat, off_lon):
    off_point = np.array([[off_lat, off_lon]])
    corrected_point = model.predict(off_point)
    return corrected_point[0]

# Example usage
off_lat, off_lon = 35.770804, -78.675410
corrected_lat_lon = adjust_lat_lon(off_lat, off_lon)
print(f'Corrected Latitude and Longitude: {corrected_lat_lon}')
