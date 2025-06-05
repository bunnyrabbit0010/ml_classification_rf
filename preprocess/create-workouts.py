import xml.etree.ElementTree as ET
import csv

xml_path = 'src-data.xml'
output_csv = 'workouts.csv'

# Mapping from HealthKit type → short label
TYPE_MAPPING = {
    'HKWorkoutActivityTypeFunctionalStrengthTraining': 'Strength Training',
    'HKWorkoutActivityTypeRunning':                     'Running',
    'HKWorkoutActivityTypeWalking':                     'Walking',
    'HKWorkoutActivityTypeCycling':                     'Cycling',
    'HKWorkoutActivityTypeYoga':                       'Yoga',
    'HKWorkoutActivityTypeHighIntensityIntervalTraining': 'HIIT',
    'HKWorkoutActivityTypeRunning':                     'Running',
    'HKWorkoutActivityTypeElliptical':                 'Elliptical',
    'HKWorkoutActivityTypeCooldown':                 'Cooldown',
    'HKWorkoutActivityTypeCoreTraining':                 'Core Training',
    'HKWorkoutActivityTypeRowing':                     'Rowing',
    'HKWorkoutActivityTypeCardioDance':                 'Cardio Dance',
    'HKWorkoutActivityTypeStairClimbing':                 'Stair Climbing',
    'HKWorkoutActivityTypeHiking':                     'Hiking',
    'HKWorkoutActivityTypeOther':                     'Other',
    'HKWorkoutActivityTypeKickboxing':                 'Kickboxing',
    'HKWorkoutActivityTypePilates':                     'Pilates'
}

INDOOR_TYPES = {
    'HKWorkoutActivityTypeFunctionalStrengthTraining', 'HKWorkoutActivityTypeYoga', 'HKWorkoutActivityTypeHighIntensityIntervalTraining',
    'HKWorkoutActivityTypeCoreTraining', 'HKWorkoutActivityTypeRowing', 'HKWorkoutActivityTypeCardioDance',
    'HKWorkoutActivityTypeStairClimbing', 'HKWorkoutActivityTypeKickboxing', 'HKWorkoutActivityTypePilates', 'HKWorkoutActivityTypeCycling'
}
 

with open(output_csv, 'w', newline='') as csvfile:
    print
    writer = csv.DictWriter(csvfile, fieldnames=[
        'workout_type','start_timestamp','end_timestamp','duration_min','source_name','source_version','device_model',
        'creation_timestamp','active_energy_kcal','basal_energy_kcal','distance_mi',
        'is_indoor','avg_mets','weather_temp_f','weather_humidity_pct','time_zone','num_segments'
    ])
    writer.writeheader()

    print(f"Parsing XML and writing to {output_csv}...")
    count = 0
    context = ET.iterparse(xml_path, events=('start',))
    for event, elem in context:
        if elem.tag == 'Workout':
            long_type = elem.attrib.get('workoutActivityType', '')
            short_label = TYPE_MAPPING.get(long_type, long_type)  # fallback to the original if not mapped
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
                'device_model': None,  # parse from elem.attrib.get('device')
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

            # Parse child tags
            for child in elem:
                if child.tag == 'WorkoutStatistics':
                    t = child.attrib.get('type')
                    if t == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                        row['active_energy_kcal'] = float(child.attrib.get('sum', 0))
                    elif t == 'HKQuantityTypeIdentifierBasalEnergyBurned':
                        row['basal_energy_kcal'] = float(child.attrib.get('sum', 0))
                    elif t == 'HKQuantityTypeIdentifierDistanceWalkingRunning':
                        # convert to miles if needed
                        row['distance_mi'] = float(child.attrib.get('sum', 0))
                elif child.tag == 'MetadataEntry':
                    k = child.attrib.get('key')
                    v = child.attrib.get('value')
                    if k == 'HKIndoorWorkout':
                        if long_type in INDOOR_TYPES:
                            row['is_indoor'] = 1
                        else:
                            row['is_indoor'] = int(v)
                    elif k == 'HKAverageMETs':
                        # strip " kcal/hr·kg"
                        row['avg_mets'] = float(v.split()[0])
                    elif k == 'HKWeatherTemperature':
                        row['weather_temp_f'] = float(v.split()[0])
                    elif k == 'HKWeatherHumidity':
                        # "5100 %" → 51.00
                        row['weather_humidity_pct'] = float(v.replace('%','')) / 100
                    elif k == 'HKTimeZone':
                        row['time_zone'] = v
                elif child.tag == 'WorkoutEvent':
                    row['num_segments'] += 1

            # You can parse device_model here if you want:
            device_str = elem.attrib.get('device', '')
            # e.g., find "model:Watch3,1" inside that string
            if 'model:' in device_str:
                # crude parsing (improve as needed)
                start = device_str.index('model:') + len('model:')
                end = device_str.find(',', start)
                row['device_model'] = device_str[start:end]

            writer.writerow(row)
            elem.clear()
    print(f"Finished parsing {count} workouts. Data written to {output_csv}.")
    print("Done.")
    csvfile.flush()
    csvfile.close()
    print(f"CSV file {output_csv} created successfully.")


    