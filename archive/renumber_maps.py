######## MAP RENUMBERING ########
import json
import pandas as pd

with open(R'C:\Users\Josh\Downloads\Maps\ZMA.json') as data_file:    
    data = json.load(data_file)
    
map_data = pd.read_csv(R'C:\Users\Josh\Downloads\Maps\pbi_maps.csv')

map_titles = list(map_data['map_title'])
map_mnemonics = list(map_data['mnemonic'])
for i in range(0, len(data['videoMaps'])): 
    m = data['videoMaps'][i]

    if 'STARS' in m['tags'] and 'PBI' in m['tags']: 
        rvm_name = 'RVM' + m['name'][0:3] + m['name'][4:8]
        if rvm_name in map_titles:
            idx = map_titles.index(rvm_name)
            title = map_data[idx:idx+1]['map_title'].to_string(index=False)
            num = map_data[idx:idx+1]['map_number'].to_string(index=False)
            short = map_data[idx:idx+1]['mnemonic'].to_string(index=False)
            short = short.replace('_', ' ').strip()

            m['shortName'] = short
            m['starsId'] = num
            print(m['starsId'], m['shortName'], sep='\t')
        else:
            found = False
            for j in range(0, len(map_titles)):
                if m['shortName'] in map_titles[j] or \
                    m['shortName'].replace(' ', '-') in map_mnemonics[j]:
                    found = True
                    idx = j
                    title = map_data[idx:idx+1]['map_title'] \
                        .to_string(index=False)
                    num = map_data[idx:idx+1]['map_number'] \
                        .to_string(index=False)
                    short = map_data[idx:idx+1]['mnemonic'] \
                        .to_string(index=False)
                    short = short.replace('_', ' ').strip()
                    m['shortName'] = short
                    m['starsId'] = num
                    print(m['starsId'], m['shortName'], '***', sep='\t')
                
            if not found:
                print('X ' + str(m['starsId']), m['shortName'], sep='\t')

data = json.dumps(data, indent=4)
with open(r'C:\Users\Josh\Downloads\Maps\ZMA_out.json', 'w') as out_file:
    print(data, file=out_file)