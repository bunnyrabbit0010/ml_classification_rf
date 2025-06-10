import boto3
import xml.etree.ElementTree as ET
from collections import defaultdict
import botocore
import yaml

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

def count_tag_attribute_from_s3(s3_uri, tag_name, attribute_name):
    s3 = boto3.client('s3')
    bucket_name, key = parse_s3_uri(s3_uri)

    try:
        print(f"Fetching file from S3: s3://{bucket_name}/{key}")
        s3_response = s3.get_object(Bucket=bucket_name, Key=key)
        print("File fetched. Starting XML parsing...")
    except botocore.exceptions.ClientError as e:
        print(f"Error fetching file from S3: {e}")
        raise

    counts = defaultdict(int)
    try:
        context = ET.iterparse(s3_response['Body'], events=('start',))
        for event, elem in context:
            if elem.tag == tag_name:
                attr_value = elem.attrib.get(attribute_name)
                if attr_value:
                    counts[attr_value] += 1
            elem.clear()

        print("XML parsing completed.")
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during XML parsing: {e}")
        raise

    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


# --- Main Script ---
if __name__ == "__main__":
    try:
        config = load_config()

        # Example: Count Workout types
        print("\nCounting Workout Activity Types...")
        workout_counts = count_tag_attribute_from_s3(
            config['s3']['source_uri'],
            tag_name=config['parse']['tag_name'],
            attribute_name=config['parse']['attribute_name']
        )

        print(" Workout Activity Type Counts:")
        for k, v in workout_counts.items():
            print(f"{k}: {v}")

    except Exception as e:
        print(f"Script failed: {e}")
