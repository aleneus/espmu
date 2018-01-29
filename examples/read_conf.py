import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from espmu.streaming import PmuStreamDataReader

reader = PmuStreamDataReader()

ip = "192.168.0.237"
tcp_port = 4712
idcode = 1

reader.connect(ip, tcp_port, idcode)

if reader.is_time_reliable():
    print("Time is reliable")
else:
    print("Time is not reliable")
    
ss = reader.stations()

fs = reader.rate()
print("fs={} Hz\n".format(fs))

# for s, i in zip(ss, range(len(ss))):
#     qs = reader.quants(i)
#     print("{}: {}\n".format(s, qs))
    
reader.disconnect()
