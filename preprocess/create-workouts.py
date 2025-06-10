import xml.etree.ElementTree as ET
import csv
import yaml
import boto3
import botocore
import os

def load_config(config_path='../config/s3_config.yml'):
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            print("Config loaded successfully.")
            return config
    except Exception as e:
        print(f"Failed to load config file: {e}")
        raise

def parse_s3_uri(s3_uri):
    try:
        parts = s3_uri.split("/")
        bucket = parts[2]
        key = "/".join(parts[3:])
        print(f"Parsed S3 URI - Bucket: {bucket}, Key: {key}")
        return bucket, key
    except Exception as e:
        print(f"Error parsing S3 URI: {e}")
        raise

TYPE_MAPPING = {
    'HKWorkoutActivityTypeFunctionalStrengthTraining': 'Strength Training',
    'HKWorkoutActivityTypeRunning': 'Running',
    'HKWorkoutActivityTypeWalking': 'Walking',
    'HKWorkoutActivityTypeCycling': 'Cycling',
    'HKWorkoutActivityTypeYoga': 'Yoga',
    'HKWorkoutActivityTypeHighIntensityIntervalTraining': 'HIIT',
    'HKWorkoutActivityTypeElliptical': 'Elliptical',
    'HKWorkoutActivityTypeCooldown': 'Cooldown',
    'HKWorkoutActivityTypeCoreTraining': 'Core Training',
    'HKWorkoutActivityTypeRowing': 'Rowing',
    'HKWorkoutActivityTypeCardioDance': 'Cardio Dance',
    'HKWorkoutActivityTypeStairClimbing': 'Stair Climbing',
    'HKWorkoutActivityTypeHiking': 'Hiking',
    'HKWorkoutActivityTypeOther': 'Other',
    'HKWorkoutActivityTypeKickboxing': 'Kickboxing',
    'HKWorkoutActivityTypePilates': 'Pilates'
}

INDOOR_TYPES = {
    'HKWorkoutActivityTypeFunctionalStrengthTraining', 'HKWorkoutActivityTypeYoga', 'HKWorkoutActivityTypeHighIntensityIntervalTraining',
    'HKWorkoutActivityTypeCoreTraining', 'HKWorkoutActivityTypeRowing', 'HKWorkoutActivityTypeCardioDance',
    'HKWorkoutActivityTypeStairClimbing', 'HKWorkoutActivityTypeKickboxing', 'HKWorkoutActivityTypePilates', 'HKWorkoutActivityTypeCycling'
}

def create_workout_csv(s3_uri, output_csv_path):
    s3 = boto3.client('s3')
    bucket_name, key = parse_s3_uri(s3_uri)

    try:
        print(f"Fetching file from S3: s3://{bucket_name}/{key}")
        s3_response = s3.get_object(Bucket=bucket_name, Key=key)
        print("File fetched. Starting XML parsing...")
    except botocore.exceptions.ClientError as e:
        print(f"Error fetching file from S3: {e}")
        raise

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'workout_type','start_timestamp','end_timestamp','duration_min','source_name','source_version','device_model',
            'creation_timestamp','active_energy_kcal','basal_energy_kcal','distance_mi',
            'is_indoor','avg_mets','weather_temp_f','weather_humidity_pct','time_zone','num_segments'
        ])
        writer.writeheader()

        count = 0
        context = ET.iterparse(s3_response['Body'], events=('start',))
        for event, elem in context:
            if elem.tag == 'Workout':
                long_type = elem.attrib.get('workoutActivityType', '')
                short_label = TYPE_MAPPING.get(long_type, long_type)
                count += 1
                if count % 100 == 0:
                    print(f"Processed {count} workouts...")
                row = {
                    'workout_type':    short_label,
                    'start_timestamp': elem.attrib.get('startDate'),
                    'end_timestamp': elem.attrib.get('endDate'),
                    'duration_min': float(elem.attrib.get('duration', 0)),
                    'source_name': elem.attrib.get('sourceName'),
                    'source_version': elem.attrib.get('sourceVersion'),
                    'device_model': None,
                    'creation_timestamp': elem.attrib.get('creationDate'),
                    'active_energy_kcal': None,
                    'basal_energy_kcal': None,
                    'distance_mi': None,
                    'is_indoor': None,
                    'avg_mets': None,
                    'weather_temp_f': None,
                    'weather_humidity_pct': None,
                    'time_zone': None,
                    'num_segments': 0,
                }

                for child in elem:
                    if child.tag == 'WorkoutStatistics':
                        t = child.attrib.get('type')
                        if t == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                            row['active_energy_kcal'] = float(child.attrib.get('sum', 0))
                        elif t == 'HKQuantityTypeIdentifierBasalEnergyBurned':
                            row['basal_energy_kcal'] = float(child.attrib.get('sum', 0))
                        elif t == 'HKQuantityTypeIdentifierDistanceWalkingRunning':
                            row['distance_mi'] = float(child.attrib.get('sum', 0))
                    elif child.tag == 'MetadataEntry':
                        k = child.attrib.get('key')
                        v = child.attrib.get('value')
                        if k == 'HKIndoorWorkout':
                            row['is_indoor'] = 1 if long_type in INDOOR_TYPES else int(v)
                        elif k == 'HKAverageMETs':
                            row['avg_mets'] = float(v.split()[0])
                        elif k == 'HKWeatherTemperature':
                            row['weather_temp_f'] = float(v.split()[0])
                        elif k == 'HKWeatherHumidity':
                            row['weather_humidity_pct'] = float(v.replace('%','')) / 100
                        elif k == 'HKTimeZone':
                            row['time_zone'] = v
                    elif child.tag == 'WorkoutEvent':
                        row['num_segments'] += 1

                device_str = elem.attrib.get('device', '')
                if 'model:' in device_str:
                    start = device_str.index('model:') + len('model:')
                    end = device_str.find(',', start)
                    row['device_model'] = device_str[start:end]

                writer.writerow(row)
                elem.clear()

    print(f"Finished parsing {count} workouts.")
    print(f"CSV saved locally to {output_csv_path}")

# --- Main Script ---
if __name__ == "__main__":
    try:
        config = load_config()
        output_path = os.path.join(os.path.dirname(__file__), '../data/workouts.csv')
        create_workout_csv(config['s3']['source_uri'], output_path)
    except Exception as e:
        print(f"Script failed: {e}")
