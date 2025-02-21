import os
import json

profiles_dir = os.getenv('LOCALAPPDATA') + os.sep + 'CRC' + os.sep + 'Profiles'

for filename in os.listdir(profiles_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(profiles_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if 'InvertNumericKeypad' in data:
            if data['InvertNumericKeypad']:
                data['InvertNumericKeypad'] = None
            else:
                data['InvertNumericKeypad'] = True

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)