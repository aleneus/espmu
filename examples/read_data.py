import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from time import sleep

from espmu.streaming import PmuStreamDataReader

reader = PmuStreamDataReader()

ip = "192.168.0.237"
tcp_port = 4713
idcode = 1

reader.connect(ip, tcp_port, idcode)

names = {
    'U' : 'Uphs_{}',
    'I' : 'Iphs_{}',
}

reader.set_phasor_names(0, names)

reader.start()

for i in range(50):
    sample = reader.get_sample_dict(0)
    t = sample['t']
    f = sample['f']
    ua = sample['a']['U']
    pa = sample['a']['P']
    qa = sample['a']['Q']
    print(t, f, ua, pa, qa)

reader.stop()
sleep(1)

reader.disconnect()
