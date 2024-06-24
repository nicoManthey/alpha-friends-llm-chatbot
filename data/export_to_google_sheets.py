
import pandas as pd
import json
from pathlib import Path

"""
Export the phq9_data to a CSV file that can be uploaded to Google Sheets.
"""

# Get the parent directory of the current file
current_file = Path(__file__)
data_dir = current_file.parent / "phq9"
print("data dir is: ", data_dir)

# Get all JSON files in the parent directory
json_files = sorted(list(data_dir.glob("q*.json")))
json_file_names = [file.name for file in json_files]
print(json_file_names)

# Initialize an empty list to store all dictionaries
combined_data = []

# Initialize lists to hold the DataFrame rows
roles = []
contents = []
case_ids = []

# Loop through each JSON file
for json_file in json_files:
    # Open the JSON file and load its data
    with open(json_file, "r") as f:
        data = json.load(f)
        # Append the data to the combined_data list
        combined_data.extend(data)

# Step 2: Iterate over each dictionary in the JSON object
for case_id, entry in enumerate(combined_data, start=1):
    # System
    if 'system' in entry:
        roles.append('system')
        contents.append(entry['system'])
        case_ids.append(case_id)

    # History
    if 'history' in entry and len(entry['history']) > 0:
        # Ensure history has an even number of entries
        for sub_entry in entry['history']:
            try:
                assert len(sub_entry) == 2, "History length is not divisible by 2"
                roles.append('user')
                contents.append(sub_entry[0])
                case_ids.append(case_id)

                roles.append('assistant')
                contents.append(sub_entry[1])
                case_ids.append(case_id)
            except AssertionError as e:
                print(f"AssertionError for case_id: {case_id}, history: {entry['history']}, error: {e}")

    # User (Instruction)
    if 'instruction' in entry:
        roles.append('user')
        contents.append(entry['instruction'])
        case_ids.append(case_id)

    # Assistant (Output)
    if 'output' in entry:
        roles.append('assistant')
        contents.append(entry['output'])
        case_ids.append(case_id)


# Step 3: Construct the DataFrame
df = pd.DataFrame({
    'case_id': case_ids,
    'role': roles,
    'content': contents
})

# Optional: Save the DataFrame to a CSV file
df.to_csv(data_dir / 'chatbot_data.csv', index=False)