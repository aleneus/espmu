import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from time import sleep, gmtime, strftime
import numpy as np

from espmu.streaming import PmuStreamDataReader

reader = PmuStreamDataReader()

ip = "192.168.0.237"
tcp_port = 4712
idcode = 1

reader.connect(ip, tcp_port, idcode)

if not reader.is_time_reliable():
    print("Time is not reliable")
    exit()

reader.setup_output(
    station_ind = 0,
    freq=True,
    phasors=['Uphs_a', 'Iphs_a', 'Uphs_b', 'Iphs_b', 'Uphs_c', 'Iphs_c']
)

reader.start()

for i in range(20):
    sample = reader.get_data(station_ind=0)
    t = sample['t']
    t = strftime("%Y-%m-%d %H:%M:%S:{}".format(round(1000*(t%1))), gmtime(t))
    ps = sample['phasors']
    ua = ps[0][0]
    ub = ps[2][0]
    uc = ps[4][0]
    pa = ps[0][0] * ps[1][0] * np.cos(ps[0][1] - ps[1][1])
    qa = ps[0][0] * ps[1][0] * np.sin(ps[0][1] - ps[1][1])
    pb = ps[2][0] * ps[3][0] * np.cos(ps[2][1] - ps[3][1])
    qb = ps[2][0] * ps[3][0] * np.sin(ps[2][1] - ps[3][1])
    pc = ps[4][0] * ps[5][0] * np.cos(ps[4][1] - ps[5][1])
    qc = ps[4][0] * ps[5][0] * np.sin(ps[4][1] - ps[5][1])
    
    print("t:", t)
    print("f:", sample['freq'])
    print("U:", ua, ub, uc)
    print("P:", pa, pb, pc)
    print("Q:", qa, qb, qc)
    print()

reader.stop()
sleep(1)

reader.disconnect()
