import os
import json
import sys
from datetime import datetime, timedelta

# Find the path to the text file
def find_txt_file(data_dir="../data"):  
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            return os.path.join(data_dir, file_name)
    raise FileNotFoundError("No .txt file found in the data directory")

# Get the text file path from command line or search for it
txt_file_path = sys.argv[1] if len(sys.argv) > 1 else find_txt_file()

# Define the base directory of the project
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Relative output path
output_json_path = os.path.join(base_dir, "output", "fhir_observations.json")

print(f"Processing file: {txt_file_path}")
print(f"Output file will be saved to: {output_json_path}")

# Function to convert text file to JSON
def process_txt_to_json(txt_file_path, output_json_path):
    try:
        # Read data from the text file
        with open(txt_file_path, "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()

        # Skip headers and unnecessary data
        data_lines = [line for line in lines if not line.startswith("#")]

        # Extract relevant columns of data
        sequence_numbers = []
        ecg_data = []

        for line in data_lines:
            columns = line.strip().split("\t")
            if len(columns) > 6:  # Ensure there's an ECG data column
                sequence_numbers.append(float(columns[0]))  # Sequence number
                ecg_data.append(float(columns[6]))  # ECG data

        # Prepare data for JSON output
        sampling_rate = 100  # Sampling rate
        time_step = 1 / sampling_rate
        start_time = datetime(2025, 1, 20)  # Initial time

        timestamps = [
            start_time + timedelta(seconds=seq * time_step)
            for seq in sequence_numbers
        ]

        fhir_observations = [
            {
                "resourceType": "Observation",
                "id": str(int(seq_num)),
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/observation-category",
                                "code": "vital-signs",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "85354-9",
                            "display": "ECG",
                        }
                    ]
                },
                "subject": {"reference": "Patient/1"},
                "effectiveDateTime": timestamp.isoformat(),
                "valueQuantity": {
                    "value": ecg_data[i],
                    "unit": "mV",
                    "system": "http://unitsofmeasure.org",
                    "code": "mV",
                },
            }
            for i, (seq_num, timestamp) in enumerate(zip(sequence_numbers, timestamps))
        ]

        # Write JSON file
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(fhir_observations, json_file, indent=4, ensure_ascii=False)

        print(f"JSON file has been saved to {output_json_path}")

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

# Call the function
process_txt_to_json(txt_file_path, output_json_path)
