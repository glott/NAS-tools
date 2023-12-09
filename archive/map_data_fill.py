#### INPUT MAP DATA FILE ####

map_data = r'C:\Users\Josh\Downloads\map_data.csv'

##### DO NOT EDIT BELOW #####

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import warnings, subprocess, sys, os, time
warnings.filterwarnings('ignore', category=DeprecationWarning)

sys.stdout = Unbuffered(sys.stdout)

try:
    import imp
    imp.find_module('pyautogui')
    imp.find_module('pyperclip')
    os.system('cls')
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'pyautogui']);
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'pyperclip']);
    os.system('cls')
    
import pyautogui as ag
import pyperclip, csv

def find_line(text, val):
    i = 0
    for line in text.split('\n'):
        if '\t' + val[0:8] in line:
            return i
        i += 1
    return -1

def fill_map(map_name, map_id, short_name, stars_category, long_name=''):
    ag.press('tab', presses=3)
    ag.hotkey('ctrl', 'a')
    ag.hotkey('ctrl', 'c')
    ag.press('tab')
    map_line = find_line(pyperclip.paste(), map_name)
    if map_line == -1:
        ag.keyDown('shift')
        ag.press('tab', presses=4)
        ag.keyUp('shift')
        print('Map \'' + map_name + '\' not found')
        return
    ag.press('tab', presses=(4 * map_line - 79) + 2)
    ag.press('enter')
    # Fill in appropriate information
    print('Attempting to write data for \'' + map_name + '\'')
    ag.press('tab', presses=1)
    if len(long_name) > 0:
        ag.write(long_name)
    ag.press('tab', presses=5)
    ag.write(str(int(map_id)))
    ag.press('tab')
    ag.write(short_name)
    ag.press('tab')
    ag.write(stars_category)
    # Toggle 'Always Visible' twice to force save
    ag.press(['tab', 'space', 'tab', 'tab', 'enter'])
    time.sleep(3)
    ag.keyDown('shift')
    ag.press('tab', presses=2)
    ag.keyUp('shift')
    ag.press(['space', 'tab', 'tab', 'enter'])
    time.sleep(3)
    ag.hotkey('shift', 'tab')
    # Save and return to 'Search...' cell
    ag.press('enter')
    time.sleep(3)
    ag.hotkey('ctrl', 'a')
    ag.press('home')
    ag.press('tab', presses=13)

f_md = open(map_data, 'r')
data = f_md.read()
f_md.close

print('####### vNAS Video Map Data Filler #######')
print('Select the \'Search...\' cell immediately!')
for i in range(5, 0, -1):
    print('You have {0} seconds before the program starts!          '
          .format(i), end='\r')
    time.sleep(1)
print('Beginning to write data                                        ')

for line in data.split('\n')[1:]:
    a = line.split(',')
    if len(a) > 4:
        fill_map(a[0], int(a[1]), a[2], a[3], long_name=a[4])
    else:
        fill_map(a[0], int(a[1]), a[2], a[3])

print('Map data filling complete!')