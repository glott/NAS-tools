#############################
###### rename_maps.py #######
#############################

######## INPUT ARTCC ########

ARTCC = 'ZOA'

##### DO NOT EDIT BELOW #####

import os, json, shutil

crc_maps = os.getenv('LOCALAPPDATA') + '\\CRC\\VideoMaps\\' + ARTCC
artcc_json = os.getenv('LOCALAPPDATA') + '\\CRC\\ARTCCs\\' + ARTCC + '.json'

f = open(artcc_json, 'r')
data = json.loads(f.read())
f.close

maps = {}
for m in data['videoMaps']:
    maps[m['id']] = m['sourceFileName']

dir_out = os.path.expanduser('~') + '\\Downloads\\' + ARTCC + ' Maps\\'

if not os.path.exists(dir_out):
    os.mkdir(dir_out)

for file in os.listdir(crc_maps):
    f = os.path.join(crc_maps, file)
    if os.path.isfile(f):
        n = f.split('\\')[-1].replace('.geojson', '')
        if n in maps:
            f_out = dir_out + maps[n]
            shutil.copy2(f, f_out)