# TODO: doc

import time
from espmu import tools as pt
from espmu.client import Client
from espmu.pmuDataFrame import DataFrame

class PmuStreamDataReader:
    def __init__(self):
        # TODO: doc
        self.idcode = None
        self.ip = None
        self.tcp_port = None
        self.cli = None
        self.station_index = None
        self.__data_on = False

    def connect(self, ip, tcp_port, idcode):
        # TODO: doc
        self.idcode = idcode
        self.conf_frame = None
        self.cli = Client(ip, tcp_port, proto="TCP")
        self.cli.setTimeout(5)
        pt.turnDataOff(self.cli, idcode)
        while not self.conf_frame:
            pt.requestConfigFrame2(self.cli, idcode)
            self.conf_frame = pt.readConfigFrame2(self.cli)

    def is_time_reliable(self):
        """ Check time quality flag and return False if time is not reliable, else True. """
        if self.conf_frame.tq == 15:
            return False
        return True

    def disconnect(self):
        # TODO: doc
        if self.cli:
            self.cli.stop()
            self.cli = None

    def start(self):
        # TODO: doc
        pt.turnDataOn(self.cli, self.idcode)
        self.__data_on = True
        
    def stop(self):
        # TODO: doc
        pt.turnDataOff(self.cli, self.idcode)
        self.__data_on = False
        
    def get_sample(self):
        # TODO: doc
        data_sample = pt.getDataSample(self.cli)
        data_frame = DataFrame(data_sample, self.conf_frame)
        secs = data_frame.soc.secCount
        msecs = data_frame.fracsec / data_frame.configFrame.time_base.baseDecStr
        x = data_frame.pmus[self.station_index].freq
        t = secs + msecs
        return x, t

    def stations(self):
        # TODO: doc
        if not self.conf_frame:
            return None
        ss = self.conf_frame.stations
        return [s.stn.replace(" ","") for s in ss]

    def quants(self, station_index):
        # TODO: doc
        if not self.conf_frame:
            return None
        ss = self.conf_frame.stations
        qs = [q.replace(" ","") for q in ss[station_index].channels]
        return qs

    def rate(self):
        return self.conf_frame.datarate
    
    def is_data_on(self):
        # TODO: doc
        return self.__data_on
