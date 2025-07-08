######## GENERATE ULID ########
import time, subprocess, warnings, sys

warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import imp
    imp.find_module('python-ulid')
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-ulid'])
    
from ulid import ULID

def gen_ulid():
    return ULID.from_timestamp(time.time())

N = 5
for i in range(0, N):
    if i % 2 == 0 and i > 0: 
        print()
    print(str(i + 1) + '\t' + str(gen_ulid()))