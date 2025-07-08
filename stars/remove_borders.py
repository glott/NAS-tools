#####################################################################
######################### remove_borders.py #########################
#####################################################################

######################## MODIFY THESE VALUES ########################
CENTER  = [38.07458, -121.00385833]               # POINT OF TANGENCY
R_TOL   = 0.005                                   # REMOVAL TOLERANCE

######### If the map border (a rectangular box) is visible ##########
#########   on your map, set EST_RAD and EST_POT to True   ##########
RADIUS  = 250.0                                   # RADIUS
EST_RAD = False                                   # ESTIMATE RADIUS
EST_POT = False                                   # ESTIMATE POT

IN_DIR  = R'C:\Users\Josh\Downloads\ZOA Maps\FAT' # INPUT DIRECTORY
OUT_DIR = 'OUTPUT'                                # OUTPUT DIRECTORY

###### These alternative POTs can be used when EST_POT is True ######
CENTER2 = [38.07458, -121.00385833]               # ALTERNATIVE POT 2
CENTER3 = [36.776111, -119.718056]                # ALTERNATIVE POT 3
CENTER4 = [37.142778, -120.324722]                # ALTERNATIVE POT 4
CENTER5 = [0, 0]                                  # ALTERNATIVE POT 5

######################### DO NOT EDIT BELOW #########################
import os, math, re, json

OUT_DIR = os.path.join(IN_DIR, OUT_DIR)
POT = [0, 0]
ALT_CENTERS = [CENTER2, CENTER3, CENTER4, CENTER5]

def dist(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) \
        * math.sin(dlon / 2) ** 2
    return 2 * math.asin(math.sqrt(a)) * 3440.07

if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

print('============ BOUNDARY REMOVER =============')
print(f'Defined POT\t [{CENTER[0]:.6f}, {CENTER[1]:.6f}]\n')
    
for file in os.listdir(IN_DIR):
    if not file.split('.')[-1] == 'geojson':
        continue
        
    with open(IN_DIR + '\\' + file, 'r') as f:
        data = json.load(f)
        print(file.split('.')[0])
        
        max_bound = [0, -1000, -1000, 1000, 1000] # [d, N, E, S, W]
        for feat in data['features']:
            if 'properties' in feat:
                if 'isTextDefaults' in feat['properties'] or \
                    'isLineDefaults' in feat['properties'] or \
                    'isSymbolDefaults' in feat['properties']:
                    continue
            for lon, lat in feat['geometry']['coordinates']:
                if lat > max_bound[1]:
                    max_bound[1] = lat
                if lat < max_bound[3]:
                    max_bound[3] = lat
                if lon > max_bound[2]:
                    max_bound[2] = lon
                if lon < max_bound[4]:
                    max_bound[4] = lon
                    
        med = [(max_bound[1] + max_bound[3]) / 2, 
                      (max_bound[2] + max_bound[4]) / 2]
        dPOT = dist(med[0], med[1], CENTER[0], CENTER[1])
        
        print(f'\tEst POT\t [{med[0]:.6f}, {med[1]:.6f}]')
        print(f'\tΔPOT\t {dPOT:.4f} NM')
        
        if dPOT > 5 and EST_POT:
            print('\t----------- ΔPOT > 5 NM -----------')
            print('\tEnter new POT lat/lon coordinates')
            print('\tEnter \'C#\' to use predefined POTs')
            print('\t  e.g. entering \'C2\' would use')
            print('\t       CENTER2\'s coordinates')
            POT_in = [input('\t\t POT_lat\t '), input('\t\t POT_lon\t ')]
            if len(POT_in[0]) == 2 and POT_in[0][0] == 'C':
                POT = ALT_CENTERS[int(POT_in[0][1]) - 2]
            else:
                POT[0] = float(POT_in[0])
                POT[1] = float(POT_in[1])
            print(f'\tNew POT\t [{POT[0]:.6f}, {POT[1]:.6f}]')
            print('\t-----------------------------------')
        else:
            POT = CENTER[:]
                    
        for feat in data['features']:
            if 'properties' in feat:
                if 'isTextDefaults' in feat['properties'] or \
                    'isLineDefaults' in feat['properties'] or \
                    'isSymbolDefaults' in feat['properties']:
                    continue
            for lon, lat in feat['geometry']['coordinates']:
                d = dist(lat, lon, POT[0], POT[1])
                if d > max_bound[0]:
                    max_bound[0] = d
        
        max_dist = max_bound[0]
        if EST_RAD:
            RADIUS = -0.000155368 * max_dist  ** 2 \
                + 0.735566 * max_dist - 5.90975
            RADIUS = 5 * round(RADIUS / 5)
        print(f'\tD_MAX\t {max_dist:.2f} NM')
        print(f'\tRADIUS\t {RADIUS:.2f} NM')
        
        if RADIUS <= 0:
            print('\t--- RADIUS < 0 NM, IGNORING MAP ---\n')
            continue
        
        i = 0
        elem_rem = 0
        while i < len(data['features']):
            feat = data['features'][i]
            if 'properties' in feat:
                if 'isTextDefaults' in feat['properties'] or \
                    'isLineDefaults' in feat['properties'] or \
                    'isSymbolDefaults' in feat['properties']:
                    i += 1
                    continue
                    
            coords = feat['geometry']['coordinates']
            j = 0
            while j < len(coords):
                lon, lat = coords[j]
                dR = dist(lat, lon, POT[0], POT[1])
                if dR > RADIUS * (1 - R_TOL):
                    del coords[j]
                    elem_rem += 1
                    j -= 1
                j += 1
            if len(coords) == 0 or len(coords) == 1:
                del data['features'][i]
                i -= 1
            i += 1
        
        print(f'\tRemoved  {elem_rem} elements')
        
        data = json.dumps(data, separators=(',', ':'))
        
        with open(os.path.join(OUT_DIR, os.path.basename(file)), 'w+') \
            as f_out:
            print(data, file=f_out)
            print()