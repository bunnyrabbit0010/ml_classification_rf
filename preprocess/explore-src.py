from collections import defaultdict
import xml.etree.ElementTree as ET

def count_tag_attribute(xml_file_path, tag_name, attribute_name):
    counts = defaultdict(int)
    print(f"Parsing XML for <{tag_name}> elements with attribute '{attribute_name}'...")

    context = ET.iterparse(xml_file_path, events=('start',))
    for event, elem in context:
        if elem.tag == tag_name:
            attr_value = elem.attrib.get(attribute_name)
            if attr_value:
                counts[attr_value] += 1
        elem.clear()

    print("Finished parsing.")
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

print("Line 1...")
with open("src-data.xml", "r", encoding="utf-8") as f:
    print(f.readline())

print("Exploring src-data.xml...")
try:
    tree = ET.parse("./src-data.xml")
    root = tree.getroot()
    print(f"Root tag: {root.tag}")
except ET.ParseError as e:
    print("Parse error:", e)


# To get record types:
record_type_counts = count_tag_attribute("src-data.xml", tag_name="Record", attribute_name="type")

# To get workout activity types:
workout_type_counts = count_tag_attribute("src-data.xml", tag_name="Workout", attribute_name="workoutActivityType")
# Print results
print("\n******************Record Type Counts:****")
for record_type, count in record_type_counts.items():
    print(f"{record_type}: {count}")


print("\n******************Workout Activity Type Counts:***************")
for workout_type, count in workout_type_counts.items():
    print(f"{workout_type}: {count}")   