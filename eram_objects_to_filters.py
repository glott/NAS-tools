#####################################################################
#################### eram_objects_to_filters.py #####################
#####################################################################

######################## MODIFY THESE VALUES ########################

MAP_DIR = 'ZOA Geomaps'
OUT_DIR = 'ZOA Geomaps - Merged'

######################### DO NOT EDIT BELOW #########################
import csv, json, os, pathlib, re

dl_dir = os.path.join(str(pathlib.Path.home() / 'Downloads'))
in_dir = os.path.join(dl_dir, MAP_DIR)
out_dir_base = os.path.join(dl_dir, OUT_DIR)

if not os.path.exists(out_dir_base):
    os.makedirs(out_dir_base)

######################## PROCESSING FUNCTION ########################
def process_files(in_dir):
    fc_out = [{} for _ in range(21)]
    for fc in fc_out:
        fc['type']  = 'FeatureCollection'
        fc['features'] = []
    
    def add_feat_to_fc(feat, filters):
        for filt in filters:
            if feat not in fc_out[filt]['features']:
                fc_out[filt]['features'].append(feat)
    
    def add_missing_props(prop, def_prop):
        for key in def_prop:
            if not key in prop:
                prop[key] = def_prop[key]
        return prop
    
    count = 0
    for file in os.listdir(in_dir):
        if not file.endswith('.geojson'):
            continue
        data = {}
        with open(os.path.join(in_dir, file), 'r') as json_file:
            data = json.load(json_file)['features']
            def_line_prop = {}
            def_sym_prop = {}
            def_text_prop = {}
    
            for feat in data:
                if 'isLineDefaults' in feat['properties']:
                    def_line_prop = feat['properties'].copy()
                    del def_line_prop['isLineDefaults']
                if 'isSymbolDefaults' in feat['properties']:
                    def_sym_prop = feat['properties'].copy()
                    del def_sym_prop['isSymbolDefaults']
                if 'isTextDefaults' in feat['properties']:
                    def_text_prop = feat['properties'].copy()
                    del def_text_prop['isTextDefaults']
    
            for feat in data:
                t = feat['geometry']['type']
                p = feat['properties']
                if 'isLineDefaults' in p or \
                'isSymbolDefaults' in p or \
                'isTextDefaults' in p:
                    continue
                if t == 'LineString':
                    p = add_missing_props(p, def_line_prop)
                elif t == 'Point':
                    if 'text' in p:
                        if len(p['text']) > 0 and isinstance(p['text'][0], float):
                            continue
                        p = add_missing_props(p, def_text_prop)
                    else:
                        p = add_missing_props(p, def_sym_prop)

                add_feat_to_fc(feat, p['filters'])

        count += 1
        print(f'Processing {os.path.basename(in_dir)} - {count} / {len(os.listdir(in_dir))}', end='\r')

    print(f'Processing {os.path.basename(in_dir)} - {count} / {len(os.listdir(in_dir))}', end='\n')
    return fc_out

########################## MERGING FUNCTION #########################
def get_defaults(feats, defs, def_filt):
    def_feat = {'type': 'Feature', 
                    'geometry': {'type': 'Point', 'coordinates': [180, 90]},
                    'properties': {'filters': [def_filt]}}
    
    for feat in feats:
        for d in defs.keys():
            if d not in feat['properties']:
                continue
            if feat['properties'][d] not in defs[d]:
                defs[d][feat['properties'][d]] = 1
            else:
                defs[d][feat['properties'][d]] += 1

    feat = def_feat.copy()
    for d in defs.keys():
        feat['properties'][d] = max(defs[d], key = lambda x: defs[d][x])
    return feat

def remove_props(feat, def_props):
    p = feat['properties']
    del_keys = []
    for k in p:
        if k not in def_props:
            continue
        if p[k] == def_props[k]:
            del_keys.append(k)
    for dk in del_keys:
        del p[dk]
    return feat

def merge_files(fc_out, in_dir_name):
    for i in range(0, len(fc_out)):
        fc = fc_out[i].copy()

        line_feats = [f for f in fc['features'] if f['geometry']['type'] == 'LineString']
        text_sym_feats = [f for f in fc['features'] if f['geometry']['type'] == 'Point']
        text_feats = [f for f in text_sym_feats if 'text' in f['properties']]
        sym_feats = [f for f in text_sym_feats if 'text' not in f['properties']]
    
        line_defs, text_defs, sym_defs = {}, {}, {}
        fc['features'] = []
        if len(line_feats) > 0:
            defs = {'bcg': {}, 'style': {}, 'thickness': {}}
            line_defs = get_defaults(line_feats, defs, i)
            line_defs['properties']['isLineDefaults'] = True
            fc['features'].append(line_defs)
    
        if len(text_feats) > 0:
            defs = {'bcg': {}, 'size': {}, 'underline': {}, 'opaque': {}, 'xOffset': {}, 'yOffset': {}}
            text_defs = get_defaults(text_feats, defs, i)
            text_defs['properties']['isTextDefaults'] = True
            fc['features'].append(text_defs)
    
        if len(sym_feats) > 0:
            defs = {'bcg': {}, 'style': {}, 'size': {}}
            sym_defs = get_defaults(sym_feats, defs, i)
            sym_defs['properties']['isSymbolDefaults'] = True
            fc['features'].append(sym_defs)
    
        for feat in line_feats:
            fc['features'].append(remove_props(feat, line_defs['properties']))

        for feat in text_feats:
            fc['features'].append(remove_props(feat, text_defs['properties']))

        for feat in sym_feats:
            fc['features'].append(remove_props(feat, sym_defs['properties']))
        
        out_name = f'{in_dir_name} - FILTER {str(i).zfill(2)}.geojson'
        out_file = os.path.join(out_dir_base, out_name)
        
        if len(fc['features']) > 0:
            with open(out_file, 'w') as out:
                out.write(json.dumps(fc, separators=(',', ':')))
        
    print(f'Merged {in_dir_name}.')

###################### PROCESS AND MERGE FILES ######################
for file in os.listdir(in_dir):
    dir = os.path.join(in_dir, file)
    if not os.path.isdir(dir):
        continue
    fc_out = process_files(dir)
    merge_files(fc_out, file)