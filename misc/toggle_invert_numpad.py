import os
import json
import time

profiles_dir = os.getenv('LOCALAPPDATA') + os.sep + 'CRC' + os.sep + 'Profiles'

i = 0
invert_state = None
for filename in os.listdir(profiles_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(profiles_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if 'InvertNumericKeypad' not in data:
            continue

        if i == 0:
            if data['InvertNumericKeypad']:
                invert_state = None
            else:
                invert_state = True

        data['InvertNumericKeypad'] = invert_state

        i += 1

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)

if invert_state == None:
    print('Numpad not inverted!')
else:
    print('Numpad inverted!')

time.sleep(1)