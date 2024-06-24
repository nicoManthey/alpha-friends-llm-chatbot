import json
from pathlib import Path

"""
Combines the data in folder phq9_data into a single JSON file.
"""

# Get the parent directory of the current file
current_file = Path(__file__)
data_dir = current_file.parent / "phq9"
print("data dir is: ", data_dir)

# Get all JSON files in the parent directory
json_files = sorted(list(data_dir.glob("q*.json")))
print(json_files)

# Initialize an empty list to store all dictionaries
combined_data = []

# Loop through each JSON file
for json_file in json_files:
    # Open the JSON file and load its data
    with open(json_file, "r") as f:
        data = json.load(f)
        # Append the data to the combined_data list
        combined_data.extend(data)

# Write the combined data to a new JSON file
with open(data_dir / "phq9_data_full.json", "w", encoding="utf-8") as f:
    json.dump(combined_data, f, ensure_ascii=False)


