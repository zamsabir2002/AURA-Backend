import json

def load_compliances():
    file_path = 'compliance.json'
    try:
        with open(file_path, 'r') as file:
            COMPLIANCE_DATA = json.load(file)
            print("JSON data loaded successfully!")
    except FileNotFoundError:
        print(f"Error: The file was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file is not a valid JSON file.")