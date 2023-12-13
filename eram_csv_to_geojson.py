#####################################################################
####################### eram_csv_to_geojson.py ######################
#####################################################################

######################## MODIFY THESE VALUES ########################

LINE_FILE = 'ZOA Geomap - Lines.csv'
SYMBOL_FILE = 'ZOA Geomap - Symbols.csv'
TEXT_FILE = 'ZOA Geomap - Texts.csv'
ROWS_HEADER = 1
ROWS_FOOTER = 2

OUT_DIR = 'ZOA Geomaps'

######################### DO NOT EDIT BELOW #########################
import csv, json
import pandas as pd
import numpy as np
import os, pathlib
import re

def convert_coord(col):
    col_out = np.zeros((2, len(col)))
    for i in range (0, len(col)):
        coord = re.sub('[NSEW]', '', col[i]).split('/')
        for j in range(0, len(coord)):
            c = coord[j]
            d = int(c[0:2 + j])
            m = int(c[2 + j:4 + j])
            s = float(c[4 + j:6 + j] + '.' + c[6 + j:])
            q = 1 if j == 0 else -1
            col_out[j][i] = round(q * (d + m / 60 + s / 3600), 6)
    return col_out

dl_dir = os.path.join(str(pathlib.Path.home() / 'Downloads'))
out_base_dir = os.path.join(dl_dir, OUT_DIR)

line_csv = os.path.join(dl_dir, LINE_FILE)
symbol_csv = os.path.join(dl_dir, SYMBOL_FILE)
text_csv = os.path.join(dl_dir, TEXT_FILE)

created_files = []

############################# LINE DATA #############################
df = pd.read_csv(line_csv, engine='python', skiprows=ROWS_HEADER, skipfooter=ROWS_FOOTER)

df['start_lat'], df['start_lon'] = convert_coord(df['Start Lat Lon'])
df['end_lat'], df['end_lon'] = convert_coord(df['End Lat Lon'])
df = df.drop('Start Lat Lon', axis=1).drop('End Lat Lon', axis=1)
df['Filter Group'] = df['Filter Group'].fillna(0)

geomap_groups = df['Geomap Id'].unique()

for map_group in geomap_groups:
    map = df[df['Geomap Id'].str.contains(map_group)]
    group_ids = map['Group Id'].unique()

    for id in group_ids:
        m = map[map['Group Id'] == id]
        
        obj_type = m['Object Type'].unique()[0]
        
        bcg = dict(m['BCG Group'].value_counts())
        def_bcg = [k for k,v in bcg.items() if v == max(bcg.values())][0]

        filt = dict(m['Filter Group'].value_counts())
        def_filt = [k for k,v in filt.items() if v == max(filt.values())]
        def_filt = [int(float(v)) for v in def_filt]
    
        style = dict(m['Line Style'].value_counts())
        def_style = [k for k,v in style.items() if v == max(style.values())][0]
    
        thick = dict(m['Thickness'].value_counts())
        def_thick = [k for k,v in thick.items() if v == max(thick.values())][0]
    
        data = {}
        data['type'] = 'FeatureCollection'
        data['features'] = []
        def_feat = {
                    'type': 'Feature', 
                    'geometry': 
                    {
                        'type': 'Point', 
                        'coordinates': [180, 90]
                    },
                    'properties':
                    {
                        'isLineDefaults': True,
                        'bcg': def_bcg,
                        'filters': def_filt,
                        'style': def_style,
                        'thickness': def_thick
                    }
                }
        data['features'].append(def_feat)
    
        for idx, r in m.iterrows():
            feat = {
                    'type': 'Feature', 
                    'geometry': 
                    {
                        'type': 'LineString', 
                        'coordinates': []
                    },
                    'properties': {}
                }
            feat['geometry']['coordinates'] = [[r['start_lon'], r['start_lat']], [r['end_lon'], r['end_lat']]]
    
            bcg = r['BCG Group']
            if bcg != def_bcg:
                feat['properties']['bcg'] = bcg
    
            filt = [int(float(v)) for v in [r['Filter Group']]]
            if filt != def_filt:
                feat['properties']['filters'] = filt
    
            style = r['Line Style']
            if style != def_style:
                feat['properties']['style'] = style
    
            thick = r['Thickness']
            if thick != def_thick:
                feat['properties']['thickness'] = thick
    
            data['features'].append(feat)

        out_dir = os.path.join(out_base_dir, map_group)
        if not os.path.exists(out_dir):
           os.makedirs(out_dir)

        out_name = f'Object #{str(id).zfill(3)} ({obj_type}).geojson'
        out_name = map_group + '-' + out_name
        out_file = os.path.join(out_dir, out_name)
        
        with open(out_file, 'w') as out:
            print(f'{map_group} / {out_name}')
            out.write(json.dumps(data, separators=(',', ':')))
            created_files.append(out_file)

############################ SYMBOL DATA ############################
df = pd.read_csv(symbol_csv, engine='python', skiprows=ROWS_HEADER, skipfooter=ROWS_FOOTER)

df['lat'], df['lon'] = convert_coord(df['Lat Lon'])
df = df.drop('Lat Lon', axis=1)
df['Filter Group'] = df['Filter Group'].fillna(0)

geomap_groups = df['Geomap Id'].unique()

for map_group in geomap_groups:
    map = df[df['Geomap Id'].str.contains(map_group)]
    group_ids = map['Group Id'].unique()

    for id in group_ids:
        m = map[map['Group Id'] == id]
        
        obj_type = m['Object Type'].unique()[0]
        
        bcg = dict(m['BCG Group'].value_counts())
        def_bcg = int([k for k,v in bcg.items() if v == max(bcg.values())][0])

        filt = dict(m['Filter Group'].value_counts())
        def_filt = [k for k,v in filt.items() if v == max(filt.values())]
        def_filt = [int(float(v)) for v in def_filt]
    
        style = dict(m['Style'].value_counts())
        def_style = [k for k,v in style.items() if v == max(style.values())][0]
    
        size = dict(m['Font Size'].value_counts())
        def_size = int([k for k,v in size.items() if v == max(size.values())][0])

        data = {}
        data['type'] = 'FeatureCollection'
        data['features'] = []

        def_sym_feat = {
                    'type': 'Feature', 
                    'geometry': 
                    {
                        'type': 'Point', 
                        'coordinates': [180, 90]
                    },
                    'properties':
                    {
                        'isSymbolDefaults': True,
                        'bcg': def_bcg,
                        'filters': def_filt,
                        'style': def_style,
                        'size': def_size
                    }
                }
        data['features'].append(def_sym_feat)

        sym_only = False
        
        text_bcg = dict(m['Text BCG Group'].value_counts())
        def_text_bcg = [k for k,v in text_bcg.items() if v == max(text_bcg.values())]
        if len(def_text_bcg) == 0:
            sym_only = True
        else:
            def_text_bcg = int(def_text_bcg[0])

            text_filt = dict(m['Text Filters'].value_counts())
            def_text_filt = [k for k,v in text_filt.items() if v == max(text_filt.values())]
            if len(def_text_filt) > 0:
                def_text_filt = str(def_text_filt[0])
                def_text_filt = [int(float(v)) for v in def_text_filt.split(' ')]
            else:
                def_text_filt = []
            
            text_size = dict(m['Text Font Size'].value_counts())
            def_text_size = int([k for k,v in text_size.items() if v == max(text_size.values())][0])
    
            underline = dict(m['Text Underline'].value_counts())
            def_underline = 'Checked' == [k for k,v in underline.items() if v == max(underline.values())][0]
    
            xoffset = dict(m['Text XPixel Offset'].value_counts())
            def_xoff = int([k for k,v in xoffset.items() if v == max(xoffset.values())][0])
    
            yoffset = dict(m['Text YPixel Offset'].value_counts())
            def_yoff = int([k for k,v in yoffset.items() if v == max(yoffset.values())][0])
            def_text_feat = {
                        'type': 'Feature', 
                        'geometry': 
                        {
                            'type': 'Point', 
                            'coordinates': [180, 90]
                        },
                        'properties':
                        {
                            'isTextDefaults': True,
                            'bcg': def_text_bcg,
                            'filters': def_text_filt,
                            'size': def_text_size,
                            'underline': def_underline,
                            'opaque': False,
                            'xOffset': def_xoff,
                            'yOffset': def_yoff
                        }
                    }
            data['features'].append(def_text_feat)

        for idx, r in m.iterrows():
            feat = {
                    'type': 'Feature', 
                    'geometry': 
                    {
                        'type': 'Point', 
                        'coordinates': []
                    },
                    'properties': {}
                }
            feat['geometry']['coordinates'] = [r['lon'], r['lat']]
    
            bcg = int(r['BCG Group'])
            if bcg != def_bcg:
                feat['properties']['bcg'] = bcg
    
            filt = [int(float(v)) for v in [r['Filter Group']]]
            if filt != def_filt:
                feat['properties']['filters'] = filt
    
            style = r['Style']
            if style != def_style:
                feat['properties']['style'] = style
    
            size = int(r['Font Size'])
            if size != def_size:
                feat['properties']['size'] = size
    
            data['features'].append(feat)

            if not sym_only:
                if pd.isna(r['Text BCG Group']) or pd.isna(r['Text Filters']):
                    continue

                feat = {
                        'type': 'Feature', 
                        'geometry': 
                        {
                            'type': 'Point', 
                            'coordinates': []
                        },
                        'properties': {}
                    }
                feat['geometry']['coordinates'] = [r['lon'], r['lat']]
                bcg = r['Text BCG Group']
                if bcg != def_text_bcg:
                    feat['properties']['bcg'] = bcg
        
                filt = [int(float(v)) for v in str(r['Text Filters']).split(' ')]
                if filt != def_text_filt:
                    feat['properties']['filters'] = filt
        
                size = int(r['Text Font Size'])
                if size != def_text_size:
                    feat['properties']['size'] = size
                
                feat['properties']['text'] = [r['Text Strings']]

                underline = 'Checked' == r['Text Underline']
                if underline != def_underline:
                    feat['properties']['underline'] = underline

                xoff = int(r['Text XPixel Offset'])
                if xoff != def_xoff:
                    feat['properties']['xOffset'] = xoff

                yoff = int(r['Text YPixel Offset'])
                if yoff != def_yoff:
                    feat['properties']['yOffset'] = yoff
        
                data['features'].append(feat)

        out_dir = os.path.join(out_base_dir, map_group)
        if not os.path.exists(out_dir):
           os.makedirs(out_dir)

        out_name = f'Object #{str(id).zfill(3)} ({obj_type}).geojson'
        out_name = map_group + '-' + out_name
        out_file = os.path.join(out_dir, out_name)
        
        if out_file in created_files:
            with open(out_file, 'r') as json_file:
                data_in = json.load(json_file)
                for feat in data_in['features']:
                    if 'isTextDefaults' in feat['properties']:
                        if feat['properties'] != def_text_feat['properties']:
                            out_name = out_name.replace(' (', 'T (')
                            out_file = os.path.join(out_dir, out_name)
                    elif 'isSymbolDefaults' in feat['properties']:
                        if feat['properties'] != def_sym_feat['properties']:
                            out_name = out_name.replace(' (', 'S (')
                            out_file = os.path.join(out_dir, out_name)
                if 'T (' not in out_name and 'S (' not in out_name:
                    data['features'] = data_in['features'] + data['features']

        with open(out_file, 'w') as out:
            print(f'{map_group} / {out_name}')
            out.write(json.dumps(data, separators=(',', ':')))
            created_files.append(out_file)

############################ TEXT DATA ############################
df = pd.read_csv(text_csv, engine='python', skiprows=ROWS_HEADER, skipfooter=ROWS_FOOTER)

df['lat'], df['lon'] = convert_coord(df['Lat Lon'])
df = df.drop('Lat Lon', axis=1)
df['Filter Group'] = df['Filter Group'].fillna(0)

geomap_groups = df['Geomap Id'].unique()

for map_group in geomap_groups:
    map = df[df['Geomap Id'].str.contains(map_group)]
    group_ids = map['Group Id'].unique()

    for id in group_ids:
        m = map[map['Group Id'] == id]
        
        obj_type = m['Object Type'].unique()[0]

        data = {}
        data['type'] = 'FeatureCollection'
        data['features'] = []
        
        text_bcg = dict(m['BCG Group'].value_counts())
        def_text_bcg = [k for k,v in text_bcg.items() if v == max(text_bcg.values())]

        def_text_bcg = int(def_text_bcg[0])

        text_filt = dict(m['Filter Group'].value_counts())
        def_text_filt = str([k for k,v in text_filt.items() if v == max(text_filt.values())][0])
        def_text_filt = [int(float(v)) for v in def_text_filt.split(' ')]
        
        text_size = dict(m['Font Size'].value_counts())
        def_text_size = int([k for k,v in text_size.items() if v == max(text_size.values())][0])

        underline = dict(m['Underline'].value_counts())
        def_underline = 'Checked' == [k for k,v in underline.items() if v == max(underline.values())][0]

        xoffset = dict(m['XPixel Offset'].value_counts())
        def_xoff = int([k for k,v in xoffset.items() if v == max(xoffset.values())][0])

        yoffset = dict(m['YPixel Offset'].value_counts())
        def_yoff = int([k for k,v in yoffset.items() if v == max(yoffset.values())][0])
        def_text_feat = {
                    'type': 'Feature', 
                    'geometry': 
                    {
                        'type': 'Point', 
                        'coordinates': [180, 90]
                    },
                    'properties':
                    {
                        'isTextDefaults': True,
                        'bcg': def_text_bcg,
                        'filters': def_text_filt,
                        'size': def_text_size,
                        'underline': def_underline,
                        'opaque': False,
                        'xOffset': def_xoff,
                        'yOffset': def_yoff
                    }
                }
        data['features'].append(def_text_feat)

        for idx, r in m.iterrows():
            feat = {
                    'type': 'Feature', 
                    'geometry': 
                    {
                        'type': 'Point', 
                        'coordinates': []
                    },
                    'properties': {}
                }
            feat['geometry']['coordinates'] = [r['lon'], r['lat']]
            bcg = r['BCG Group']
            if bcg != def_text_bcg:
                feat['properties']['bcg'] = bcg
    
            filt = [int(float(v)) for v in str(r['Filter Group']).split(' ')]
            if filt != def_text_filt:
                feat['properties']['filters'] = filt
    
            size = int(r['Font Size'])
            if size != def_text_size:
                feat['properties']['size'] = size
            
            feat['properties']['text'] = [r['Text Strings']]

            underline = 'Checked' == r['Underline']
            if underline != def_underline:
                feat['properties']['underline'] = underline

            xoff = int(r['XPixel Offset'])
            if xoff != def_xoff:
                feat['properties']['xOffset'] = xoff

            yoff = int(r['YPixel Offset'])
            if yoff != def_yoff:
                feat['properties']['yOffset'] = yoff
    
            data['features'].append(feat)

        out_dir = os.path.join(out_base_dir, map_group)
        if not os.path.exists(out_dir):
           os.makedirs(out_dir)

        out_name = f'Object #{str(id).zfill(3)} ({obj_type}).geojson'
        out_name = map_group + '-' + out_name
        out_file = os.path.join(out_dir, out_name)
        
        if out_file in created_files:
            with open(out_file, 'r') as json_file:
                data_in = json.load(json_file)
                for feat in data_in['features']:
                    if 'isTextDefaults' in feat['properties']:
                        if feat['properties'] != def_text_feat['properties']:
                            out_name = out_name.replace(' (', 'T (')
                            out_file = os.path.join(out_dir, out_name)
                if 'T (' not in out_name:
                    data['features'] = data_in['features'] + data['features']

        with open(out_file, 'w') as out:
            print(f'{map_group} / {out_name}')
            out.write(json.dumps(data, separators=(',', ':')))