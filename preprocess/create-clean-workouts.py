import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib  # To save encoders
import os

# Step 1: Read CSV
print("📂 Reading workout data from CSV...")
csv_file = 'workouts.csv'  
df = pd.read_csv(csv_file)

# Step 2: Convert workout_type to integer using LabelEncoder
print("🔠 Encoding workout types...")  
workout_encoder = LabelEncoder()
df['workout_type_encoded'] = workout_encoder.fit_transform(df['workout_type'])

# Save workout_type mapping
print("🔢 Encoding workout types...")
os.makedirs('encoders', exist_ok=True)
joblib.dump(workout_encoder, 'encoders/workout_type_encoder.pkl')

# Step 3: Convert date-time fields to components
print("🕒 Converting date-time fields...")
datetime_cols = ['start_timestamp', 'end_timestamp']
for col in datetime_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')
    df[f'{col}_year'] = df[col].dt.year
    df[f'{col}_month'] = df[col].dt.month
    df[f'{col}_day'] = df[col].dt.day
    df[f'{col}_hour'] = df[col].dt.hour
    df[f'{col}_minute'] = df[col].dt.minute
    df[f'{col}_weekday'] = df[col].dt.weekday

# Create has_distance flag
df["has_distance"] = df["distance_mi"].notna().astype(int)

# Impute missing distance_mi with 0.0
df["distance_mi"] = df["distance_mi"].fillna(0.0)

df["active_energy_kcal"] = df["active_energy_kcal"].fillna(0.0)
df["basal_energy_kcal"] = df["basal_energy_kcal"].fillna(0.0)
df["avg_mets"] = df["avg_mets"].fillna(0.0)
df["weather_temp_f"] = df["weather_temp_f"].fillna(df["weather_temp_f"].median())
df["weather_humidity_pct"] = df["weather_humidity_pct"].fillna(df["weather_humidity_pct"].median())
df["is_indoor"] = df["is_indoor"].fillna(df["is_indoor"].mode()[0])

# Step 4: Drop unneeded fields
print("🗑️ Dropping unneeded columns...")
drop_columns = [
    'workout_type', 'start_timestamp', 'end_timestamp',
    'source_name', 'source_version', 'device_model',
    'creation_timestamp', 'num_segments'
]
df.drop(columns=drop_columns, inplace=True)

# Step 5: Encode time_zone and save mapping
print("🌐 Encoding time zones...")
tz_encoder = LabelEncoder()
df['time_zone_encoded'] = tz_encoder.fit_transform(df['time_zone'])
df.drop(columns=['time_zone'], inplace=True)

# Save time_zone encoder
print("🔒 Saving time zone encoder...")
joblib.dump(tz_encoder, 'encoders/time_zone_encoder.pkl')

# Step 6: Save cleaned/preprocessed CSV
print("💾 Saving cleaned data to CSV...")
df.to_csv('cleaned_workout_data.csv', index=False)

print("✅ Preprocessing complete. Encoded data saved to 'cleaned_workout_data.csv'.")
print("🧠 Encoders saved to 'encoders/' folder for inference use.")
