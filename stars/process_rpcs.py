#!/usr/bin/env python
# coding: utf-8

# In[ ]:


FILE_IN = 'adapt.txt'


# In[ ]:


import os, time, re, json, subprocess, sys
import importlib.util as il

if None in [il.find_spec('python-ulid'), il.find_spec('pyperclip'), il.find_spec('pandas')]:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-ulid']);
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyperclip']);
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas']);
    
from ulid import ULID
import pyperclip
import pandas as pd

def gen_ulid():
    return str(ULID.from_timestamp(time.time()))

def convert_coord(c):
    c = str(c)
    j = len(c) - 6
    d = int(c[0:2 + j])
    m = int(c[2 + j:4 + j])
    s = float(c[4 + j:6 + j] + '.' + c[6 + j:])
    q = 1 if j == 0 else -1
    coord = round(q * (d + m / 60 + s / 3600), 6)
    
    return coord

def pprint(dict):
    print(json.dumps(dict, indent=2))

def comma_followed_by_number(s):
    for i, char in enumerate(s[:-1]):
        if char == ',' and s[i+1].isdigit():
            return True
    return False

def extract_table_section_from_file(section_header, filename, offset=0):
    offset *= 3
    section_header = '******* ' + section_header + ' *******'

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    with open(os.path.join(downloads_folder, filename), "r") as file:
        lines = file.readlines()

    extracted_lines = []
    inside_section = False
    end_marker_count = 0

    for line in lines:
        if section_header in line:
            inside_section = True
            extracted_lines.append(line)
            continue

        if inside_section:
            if end_marker_count > offset:
                extracted_lines.append(line)
            # Count lines that are mostly dashes
            if line.strip().startswith('---'):
                end_marker_count += 1
                if end_marker_count >= 3 + offset:
                    break

    return "".join(extracted_lines)

def remove_dash_lines(text):
    cleaned_lines = [
        line for line in text.splitlines()
        if not line.strip().startswith("---")
    ]
    return "\n".join(cleaned_lines)

def convert_pipe_text_to_csv(multi_line_text):
    csv_lines = []
    for line in multi_line_text.splitlines():
        if not line.strip():
            continue
        if '|' not in line:
            continue
        
        fields = [field.strip() for field in line.strip('|').split('|')]
        csv_line = '|'.join(fields)
        csv_lines.append(csv_line)

    return '\n'.join(csv_lines)

def csv_text_to_dataframe(csv_text):
    lines = [line.strip() for line in csv_text.strip().split('\n') if line.strip()]
    
    headers = [h.strip() for h in lines[0].split('|')]
    
    data = []
    for line in lines[1:]:
        fields = [f.strip() for f in line.split('|')]
        data.append(fields)
    
    df = pd.DataFrame(data, columns=headers)
    return df

def read_adaptation_section(section_header, filename, offset=0):
    text = extract_table_section_from_file(section_header, filename, offset)
    text = remove_dash_lines(text)
    text = convert_pipe_text_to_csv(text)
    
    return csv_text_to_dataframe(text)


# In[ ]:


def find_scratchpads(rpcs, filename):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    with open(os.path.join(downloads_folder, filename), "r") as file:
        lines = file.readlines()

    scratchpads = {}
    for idx, row in rpcs.iterrows():
        apt = row['Airport ID']
        rid = row['RPC ID']

        start_breaking = False
        search_text = ''
        for i in range(0, len(lines)):
            if 'RPC_' + apt + '_' + rid + ' MAIN_RWY' in lines[i]:
                start_breaking = True
                search_text += lines[i] + '\n'
                continue
            
            if start_breaking:
                search_text += lines[i]
                if not('equal' in lines[i] or len(lines[i]) <= 1 or \
                    ';' in lines[i][0:int(len(lines[i]) / 2)]) or 'GHOST' in lines[i]:
                    break

        sp = re.findall(r'equal\s+scratch\s+"(.*?)"', search_text)
        scratchpads[apt + '_' + rid + '_M'] = sp

    for idx, row in rpcs.iterrows():
        apt = row['Airport ID']
        rid = row['RPC ID']

        start_breaking = False
        search_text = ''
        for i in range(0, len(lines)):
            if 'RPC_' + apt + '_' + rid + ' ALT_RWY' in lines[i]:
                start_breaking = True
                search_text += lines[i] + '\n'
                continue
            
            if start_breaking:
                search_text += lines[i]
                if not('equal' in lines[i] or len(lines[i]) <= 1 or \
                    ';' in lines[i][0:int(len(lines[i]) / 2)]) or 'GHOST' in lines[i]:
                    break

        sp = re.findall(r'equal\s+scratch\s+"(.*?)"', search_text)
        scratchpads[apt + '_' + rid + '_A'] = sp

    return scratchpads


# In[ ]:


filename = FILE_IN
rpc0 = read_adaptation_section('RWY_PAIR_CONFIG', filename)
rwy1 = read_adaptation_section('RPC_RUNWAY', filename, offset=0)
rwy2 = read_adaptation_section('RPC_RUNWAY', filename, offset=1)
rwy3 = read_adaptation_section('RPC_RUNWAY', filename, offset=2)


# In[ ]:


rpcs = []
scratchpads = find_scratchpads(rpc0, filename)

counter = 1
for index, row in rpc0.iterrows():
    a = {}
    rid = row['RPC ID']
    
    a['id'] = gen_ulid()
    a['index'] = counter
    a['airportId'] = row['Airport ID']

    a['positionSymbolStagger'], a['positionSymbolTie'] = '!', '!'
    if len(row['Stagger Mode']) > 0:
        a['positionSymbolStagger'] = row['Stagger Mode']
    if len(row['Tie Mode']) > 0:
        a['positionSymbolTie'] = row['Tie Mode']

    for i in range(0, 2):
        r_type = 'M'
        if i == 1:
            r_type = 'S'
        
        r = {}
        d1 = rwy1[(rwy1['Airport ID'] == row['Airport ID']) & 
            (rwy1['RPC ID'] == rid) & (rwy1['rwy_type'] == r_type)].iloc[0]
        rpc_num = d1['#.']
        d2 = rwy2[rwy2['#.'] == rpc_num].iloc[0]
        d3 = rwy3[rwy3['#.'] == rpc_num].iloc[0]
        
        r['runwayId'] = d1['Runway ID']
        r['headingTolerance'] = int(d1['Heading Tol'])
        
        r['nearSideHalfWidth'] = float('0' + d3['NS HW'])
        if r['nearSideHalfWidth'] < 0.01:
            r['nearSideHalfWidth'] = 0.01
        
        r['farSideHalfWidth'] = float('0' + d3['FS HW'])
        if r['farSideHalfWidth'] < 0.01:
            r['farSideHalfWidth'] = 0.01
        
        r['nearSideDistance'] = float('0' + d3['NS Dist'])
        if r['nearSideDistance'] < 0.01:
            r['nearSideDistance'] = 0.01
        
        r['regionLength'] = float('0' + d3['Region Len'])
        if r['regionLength'] < 0.01:
            r['regionLength'] = 0.01
            
        r['targetReferencePoint'] = {'lat': convert_coord(d1['Tgt Lat']), 'lon': convert_coord(d1['Tgt Long'])}
        r['targetReferenceLineHeading'] = float('0' + d2['Tgt Angle'])
        r['targetReferenceLineLength'] = int('0' + d2['Tgt Length'])
        r['targetReferencePointAltitude'] = int('0' + d2['Tgt Alt'])
        r['imageReferencePoint'] = {'lat': convert_coord(d1['Img Lat']), 'lon': convert_coord(d2['Img Long'])}
        r['imageReferenceLineHeading'] = float('0' + d2['Img Angle'])
        r['imageReferenceLineLength'] = int('0' + d2['Img Length'])
        
        r['tieModeOffset'] = float('0' + d2['Tie Offset'])
        if r['tieModeOffset'] < 0.01:
            r['tieModeOffset'] = 0.01
            
        r['descentPointDistance'] = float('0' + d2['Descent Dist'])
        if r['descentPointDistance'] < 0.01:
            r['descentPointDistance'] = 0.01
            
        r['descentPointAltitude'] = int('0' + d3['Descent Alt'])
        r['abovePathTolerance'] = int(d3['Above Tol'])
        if r['abovePathTolerance'] > 99:
            r['abovePathTolerance'] = 99
            
        r['belowPathTolerance'] = int(d3['Below Tol'])
        if r['belowPathTolerance'] > 99:
            r['belowPathTolerance'] = 99
            
        r['defaultLeaderDirection'] = str(d1['Orientation'])
        r['scratchpadPatterns'] = []

        rpc_scratch_name = a['airportId'] + '_' + rwy1['RPC ID'][0] + '_' + r_type.replace('S', 'A')
        if rpc_scratch_name in scratchpads:
            r['scratchpadPatterns'] = scratchpads[rpc_scratch_name]

        if i == 0:
            a['masterRunway'] = r
        else:
            a['slaveRunway'] = r

    rpcs.append(a)

    if counter == 1:
        pprint(a)
    
    counter += 1

downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
out_name = (rpc0['Airport ID'].mode()[0]).lower() + '_rpcs.json'
with open(os.path.join(downloads_folder, out_name), "w") as file:
    json.dump(rpcs, file, indent=4)

