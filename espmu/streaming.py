""" This module implements the class for high-level interaction with
number of PMUs (stations) whithin PDC. """

from espmu import tools as pt
from espmu.client import Client


class PmuStreamDataReader:
    """ Data reader. """
    def __init__(self):
        """ Initialization. """
        self.__idcode = None
        self.__cli = None
        self.__data_on = False
        self.__output_settings = []
        self.__conf_frame = None

    def connect(self, ip_addr, tcp_port, idcode):
        """ Connect to PDC or PMU. """
        self.__idcode = idcode
        self.__cli = Client(ip_addr, tcp_port, proto="TCP")
        self.__cli.setTimeout(5)
        if not self.__cli.connectToDest():
            return False
        pt.turnDataOff(self.__cli, idcode)
        while True:
            pt.requestConfigFrame2(self.__cli, idcode)
            answer = pt.readConfigFrame2(self.__cli)
            if answer is None:
                continue
            elif not answer:
                return False
            else:
                self.__conf_frame = answer
                break
        self.__output_settings = [None]*self.__conf_frame.num_pmu
        return True

    def disconnect(self):
        """ Disconnect from PDC or PMU. """
        if self.__cli:
            self.__cli.stop()
            self.__cli = None

    def is_data_on(self):
        """ Check if data stream is on. """
        return self.__data_on

    def is_time_reliable(self):
        """ Check time quality flag and return False if time is not
        reliable, else True. """
        if self.__conf_frame.tq == 15:
            return False
        return True

    def start(self):
        """ Start data stream. """
        pt.turnDataOn(self.__cli, self.__idcode)
        self.__data_on = True

    def stations(self):
        """ Return the names of stations. """
        if not self.__conf_frame:
            return None
        st_names = self.__conf_frame.stations
        return [st_name.stn.replace(" ", "") for st_name in st_names]

    def stop(self):
        """ Stop data stream. """
        pt.turnDataOff(self.__cli, self.__idcode)
        self.__data_on = False

    def rate(self):
        """ Return data rate. """
        return self.__conf_frame.datarate

    def phasors(self, station_ind):
        """ Return list of phasors names. """
        ph_names = self.__conf_frame.stations[station_ind].ph_channels
        res = []
        for ph_name in ph_names:
            res.append(ph_name.replace(" ", ""))
        return res

    def analogs(self, station_ind):
        """ Return list of names of analog values. """
        an_names = self.__conf_frame.stations[station_ind].an_channels
        res = []
        for an_name in an_names:
            res.append(an_name.replace(" ", ""))
        return res

    def get_full_samples(self, station_ind):
        """ Return list of samples. """
        data_sample = pt.getDataSample(self.__cli)
        data_frames = pt.get_data_frames(data_sample, self.__conf_frame)
        samples = []
        for data_frame in data_frames:
            station = data_frame.pmus[station_ind]
            secs = data_frame.soc.secCount
            msecs = data_frame.fracsec
            msecs = msecs / data_frame.configFrame.time_base.baseDecStr
            sample = [secs + msecs]
            sample.append(station.freq)
            for phasor in station.phasors:
                sample.append((phasor.mag, phasor.rad))
            for analog in station.analogs:
                sample.append(analog[1])
            samples.append(sample)
        return samples
