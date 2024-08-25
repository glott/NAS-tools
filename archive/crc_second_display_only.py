#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json, os
crc_profiles = os.getenv('LOCALAPPDATA') + R'\CRC\Profiles'

for file in os.listdir(crc_profiles):
    if '.json' not in file:
        continue
        
    f = os.path.join(crc_profiles, file)
    if file[3] != '2':
        os.rename(f, f.replace('.json', '.bak'))
        continue
    
    data = {}
    with open(f) as json_file:
        data = json.load(json_file)
        
        dws = data['DisplayWindowSettings']
        
        if len(dws) == 2:
            dws.pop(0)
        
        bounds = dws[0]['WindowSettings']['Bounds']
        dws[0]['WindowSettings']['Bounds'] =             bounds.replace('3840,550', '0,0')
        
    with open(f, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)   

