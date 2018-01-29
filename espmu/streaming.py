""" This module implements the class for high-level interaction with number of PMUs (stations) whithin PDC. """
# TODO: add to docs

import time
import numpy as np

from espmu import tools as pt
from espmu.client import Client
from espmu.pmuDataFrame import DataFrame

class PmuStreamDataReader:
    def __init__(self):
        """ Initialization. """
        self.__idcode = None
        self.__cli = None
        self.__data_on = False
        self.__output_settings = []
        self.__conf_frame = None
        self.station_index = None # TODO: deprecate

    def connect(self, ip, tcp_port, idcode):
        """ Connect to PDC or PMU. """
        self.__idcode = idcode
        self.__conf_frame = None
        self.__cli = Client(ip, tcp_port, proto="TCP")
        self.__cli.setTimeout(5)
        pt.turnDataOff(self.__cli, idcode)
        while not self.__conf_frame:
            pt.requestConfigFrame2(self.__cli, idcode)
            self.__conf_frame = pt.readConfigFrame2(self.__cli)
        self.__output_settings = [None]*self.__conf_frame.num_pmu

    def disconnect(self):
        """ Disconnect from PDC or PMU. """
        if self.__cli:
            self.__cli.stop()
            self.__cli = None

    def get_data(self, station_ind):
        """ Get sample from station. """
        settings = self.__output_settings[station_ind]
        
        data_frame = DataFrame(pt.getDataSample(self.__cli), self.__conf_frame)
        station = data_frame.pmus[station_ind]
        secs = data_frame.soc.secCount
        msecs = data_frame.fracsec / data_frame.configFrame.time_base.baseDecStr
        data = {'t': secs + msecs}
        
        if settings['return_freq']:
            data['freq'] = station.freq
            
        if len(settings['phasor_inds']) > 0:
            data['phasors'] = []
            for ind in settings['phasor_inds']:
                phasor = station.phasors[ind]
                data['phasors'].append((phasor.mag, phasor.rad if settings['radians'] else phasor.deg))

        return data
        
    def get_sample(self):
        """ Deprecated. Use get_data instead. """
        # TODO: deprecate
        data_sample = pt.getDataSample(self.__cli)
        data_frame = DataFrame(data_sample, self.__conf_frame)
        secs = data_frame.soc.secCount
        msecs = data_frame.fracsec / data_frame.configFrame.time_base.baseDecStr
        x = data_frame.pmus[self.station_index].freq
        t = secs + msecs
        return x, t

    def is_data_on(self):
        """ Check if data stream is on. """
        return self.__data_on
    
    def is_time_reliable(self):
        """ Check time quality flag and return False if time is not reliable, else True. """
        if self.__conf_frame.tq == 15:
            return False
        return True

    def setup_ouput(self, station_ind, freq=False, phasors=[], radians=True):#, analogs=[], digitals=[]):
        """ Setup the contents of outputed samples from station. """
        settings = {}
        settings['return_freq'] = freq
        ph_names = []
        for s in self.__conf_frame.stations[station_ind].ph_channels:
            ph_names.append(s.replace(" ",""))
        inds = []
        for phasor in phasors:
            inds.append(ph_names.index(phasor))
        settings['phasor_inds'] = inds
        settings['radians'] = radians
        self.__output_settings[station_ind] = settings
        return True

    def start(self):
        """ Start data stream. """
        pt.turnDataOn(self.__cli, self.__idcode)
        self.__data_on = True
        
    def stations(self):
        """ Return the names of stations. """
        if not self.__conf_frame:
            return None
        ss = self.__conf_frame.stations
        return [s.stn.replace(" ","") for s in ss]

    def stop(self):
        """ Stop data stream. """
        pt.turnDataOff(self.__cli, self.__idcode)
        self.__data_on = False
        
    def rate(self):
        """ Return data rate. """
        return self.__conf_frame.datarate
