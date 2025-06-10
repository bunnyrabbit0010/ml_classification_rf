import joblib
import pandas as pd

# Load the model and encoders
model = joblib.load('model_with_smote.joblib')
label_encoder = joblib.load('../data/encoders/workout_type_encoder.pkl')
time_zone_encoder = joblib.load('../data/encoders/time_zone_encoder.pkl')

# Load your input CSV file
df = pd.read_csv("../data/inference_inputs.csv")

# Encode time zone
df['time_zone_encoded'] = time_zone_encoder.transform(df['time_zone'])

# Drop the original string column after encoding
df = df.drop(columns=['time_zone'])

# Ensure column order matches training
feature_columns = [
    'duration_min', 'active_energy_kcal', 'basal_energy_kcal',
    'distance_mi', 'is_indoor', 'avg_mets',
    'weather_temp_f', 'weather_humidity_pct',
    'start_timestamp_year', 'start_timestamp_month', 'start_timestamp_day',
    'start_timestamp_hour', 'start_timestamp_minute', 'start_timestamp_weekday',
    'end_timestamp_year', 'end_timestamp_month', 'end_timestamp_day',
    'end_timestamp_hour', 'end_timestamp_minute', 'end_timestamp_weekday',
    'has_distance', 'time_zone_encoded'
]

input_df = df[feature_columns]

# Predict
predicted_encoded = model.predict(input_df)

# Decode predicted labels
predicted_labels = label_encoder.inverse_transform(predicted_encoded)

# Add predictions to the original input
df['predicted_workout_type'] = predicted_labels

# Save or print results
print(df[['predicted_workout_type']])

