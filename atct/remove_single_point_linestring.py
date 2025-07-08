######## REMOVE SINGLE POINT LINESTRINGS ########
import json, os

map_dir = R'C:\Users\Josh\Downloads\ZOA Maps\NCT'
out_dir = map_dir + os.sep + 'OUTPUT'

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

for file in os.listdir(map_dir):
    if not 'geojson' in file:
        continue
    with open(os.path.join(map_dir, file)) as f:
        data = json.load(f)
        i = 0
        while i < len(data['features']):
            feat_type = data['features'][i]['geometry']['type']
            coords = data['features'][i]['geometry']['coordinates']
            if len(coords) == 1 and feat_type == 'LineString':
                del data['features'][i]
                i -= 1
            i += 1
        data = json.dumps(data, separators=(',', ':'))
        
        with open(os.path.join(out_dir, os.path.basename(file)), 'w+') as f_out:
            print(data, file=f_out)