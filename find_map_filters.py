######## FIND MAPS WITH CERTAIN FILTERS ########
import json, os, shutil

map_dir = R'C:\Users\Josh\Downloads\ZMA Maps\ZMA'
out_dir = map_dir + os.sep + 'SELECT'

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

for file in os.listdir(map_dir):
    if not 'geojson' in file:
        continue
    with open(os.path.join(map_dir, file)) as f:
        data = json.load(f)
        
        for feat in data['features']:
            if 'filters' in feat['properties']:
                if 3 in feat['properties']['filters']:
                    print(file + '\t' + str(feat['properties']['filters']))
                    shutil.copy(map_dir + os.sep + file, out_dir)