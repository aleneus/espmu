import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import time

from espmu.streaming import PmuStreamDataReader

reader = PmuStreamDataReader()

ip = "192.168.0.237"
tcp_port = 4713
idcode = 1

reader.connect(ip, tcp_port, idcode)

# TODO: this is not explicit action
reader.station_index = 0

reader.start()

for i in range(50):
    f = reader.get_sample()
    print(f)

reader.stop()
time.sleep(1)

reader.disconnect()
