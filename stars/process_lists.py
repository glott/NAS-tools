FILE_IN = 'den.txt'     # File name in Downloads folder
MAIN_TCP = '1I'         # Main TCP, will output window position if found

################################################################################
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

filename = FILE_IN
send = read_adaptation_section('SENDING_FP_TCP', filename)
rec = read_adaptation_section('FLIGHT_PLAN_TCP', filename)
crd = read_adaptation_section('FLIGHT_PLAN_CRDMSG', filename)
tt1 = read_adaptation_section('TCW_TDW_LISTS', filename)
tt2 = read_adaptation_section('TCW_TDW_LISTS', filename, offset=1)
cw = read_adaptation_section('CONSOL_WINDOWS', filename)

showTitleDict = {'A': 'AlwaysDisplay', 'N': 'NeverDisplay', 'E': 'DisplayIfEntries'}
flightTypeDict = {'': 'Any', 'P': 'Departure', 'A': 'Arrival', 'E': 'Overflight'}
flight_rules = ['ALL', 'IFR', 'VFR', 'OTP', 'IFR/OTP', 'VFR/OTP']
sortFieldDict = {
        'ACID': 'AircraftId',
        'Add at End of List': 'AddAtEndOfList',
        'Add at end of list': 'AddAtEndOfList',
        'Add to end': 'AddAtEndOfList',
        'Aircraft Category': 'AircraftCategory',
        'Aircraft ID': 'AircraftId',
        'Aircraft Type': 'AircraftType',
        'Assigned Altitude': 'AssignedAltitude',
        'Assigned Beacon Code': 'AssignedBeaconCode',
        'Coord Seq': 'CoordinationSequence',
        'Coord Time': 'CoordinationTime',
        'Coordination Sequence': 'CoordinationSequence',
        'Coordination Time': 'CoordinationTime',
        'Create': 'CreationTime',
        'Creation Time': 'CreationTime',
        'Drop Zone Entry Time': 'DropZoneEntryTime',
        'DZ Entry': 'DropZoneEntryTime',
        'Entry Fix': 'EntryFix',
        'Exit Fix': 'ExitFix',
        'Flight Rules': 'FlightRules',
        'Landing Runway': 'LandingRunway',
        'Mode 3 Code': 'Mode3Code',
        'Mode C Altitude': 'ModeCAltitude',
        'NAS Code': 'NasCode',
        'Number of Aircraft': 'NumberOfAircraft',
        'Owner TCP': 'OwnerTcp',
        'Pilot Reported Level': 'PilotReportedLevel',
        'Range from Airport': 'RangeFromAirport',
        'Range': 'RangeFromAirport',
        'Scratchpad': 'Scratchpad',
        'Special Condition Code': 'SpecialConditionCode',
        'Speed': 'Speed',
        'Tcid': 'Tcid',
        'Time of Alert': 'TimeOfAlert',
        'Type of Flight': 'TypeOfFlight'
    }

data = []
list_configs = {}
info_out = []
for idx, t1 in tt1[(tt1['Title'].str.strip() != '') & (tt1['List ID'].str.startswith('P'))].iterrows():
    
    i = int(t1['#.'])
    t2 = tt2[tt2['#.'] == str(i)].iloc[0]
    c = int(t2['Coord. Channel'])

    e = {}
    e['id'] = t1['List ID']
    e['title'] = t1['Title'] # .replace('.      ', '')
    e['showTitle'] = showTitleDict[t1['Show Title']]
    e['numberOfEntries'] = int(t1['Number Entries'])
    e['persistentEntries'] = t1['Prstnt Entries'] == 'Y'
    e['showMore'] = t1['More NN/MM'] == 'Y'

    if c != 0:
        c = str(c)
        c0 = crd[crd['Channel'] == str(c)].iloc[0]
        cc = {}

        cc['id'] = gen_ulid()
        cc['airport'] = c0['Airport']
    
        cc['flightType'] = flightTypeDict[c0['Flight Type']]
        cc['flight_rules'] = flight_rules[int('0' + c0['Flight Rules'])]
    
        sending_tcps = []
        for tcp in send[send['Channel'] == c]['Sending TCPs'].tolist():
            sending_tcps.append({'subset': tcp[0], 'sectorId': tcp[1]})
        cc['sendingTcps'] = sending_tcps
    
        receiving_tcps = []
        for index, row in rec[rec['Channel'] == c].iterrows():
            receiver = {}
            tcp = row['Receiving TCP']
            receiver['key'] = gen_ulid()
            receiver['receivingTcp'] = {'subset': tcp[0], 'sectorId': tcp[1]}
            receiver['autoAcknowledge'] = row['Auto. Ack.'] == 'Y'
            receiving_tcps.append(receiver)
        cc['receivers'] = receiving_tcps
        
        e['coordinationChannel'] = cc

    e['showLineNumbers']  = t2['Line Numbers'] == 'Y'
    e['sortField'] = sortFieldDict[t2.get('Prim Sort Field', t2.get('Sort Field'))]
    e['sortIsAscending'] = t2.get('Prim Sort Dir', t2.get('Sort Direction')) == 'A'

    data.append(e)

    config_data = cw[(cw['Title'] == e['title']) & (cw['logical_tcp'] == MAIN_TCP)]
    if not config_data.empty:
        cd = {}
        cd['Visible'] = False
        cd['Location'] = config_data['Flight Left'].iloc[0] + ', ' + config_data['Flight Top'].iloc[0]
        cd['NumberOfLines'] = e['numberOfEntries']
        cd['ShowTitleUntil'] = None
        list_configs[e['id']] = cd

    info_out.append(e['id'] + '\t' + e['title'])

info_out.sort()
print('\n'.join(info_out))

downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
f = filename.replace('.txt', '')

with open(os.path.join(downloads_folder, f + '_lists.json'), "w") as file:
    json.dump(data, file, indent=4)

with open(os.path.join(downloads_folder, f + '_list_configs.json'), "w") as file:
    json.dump(list_configs, file, indent=4)

with open(os.path.join(downloads_folder, f + '_info.txt'), "w") as file:
    file.write('\n'.join(info_out))