######## LIST MAPS ########
import json

with open(R'C:\Users\Josh\Downloads\ZMA.json') as data_file:    
    data = json.load(data_file)
    
for i in range(0, len(data['videoMaps'])): 
    m = data['videoMaps'][i]
    
    if 'STARS' in m['tags'] and 'TPA' in m['tags']:
        print(str(m['starsId']) + '\t' + m['shortName'] + '\t' + m['name'])