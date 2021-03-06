"""In this module the data frame is defined."""

import math
import struct
from datetime import datetime

from espmu.pmuFrame import PMUFrame
from espmu.pmuLib import hexToBin
from espmu.pmuEnum import (DataError, PmuSync, Sorting, Trigger,
                           ConfigChange, DataModified, TimeQuality,
                           UnlockedTime, TriggerReason)


class DataFrame(PMUFrame):
    """
    Class for creating a Data Frame based on C37.118-2011

    :param frame_in_hex_str: Data frame bytes as hex str
    :type frame_in_hex_str: str
    :param config_frame: Config frame describing the data frame
    :type config_frame: ConfigFrame
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, frame_in_hex_str, config_frame, debug=False):
        self.stat = None
        self.pmus = None
        self.freq = None
        self.dfreq = None
        self.analog = None
        self.digital = None
        self.parse_pos = 0
        self.configFrame = config_frame
        self.dbg = debug
        super().__init__(frame_in_hex_str, self.dbg)
        super().finishParsing()
        self.parsePmus()
        self.updateSOC()

    def parsePmus(self):
        """Parses each PMU present in the data frame."""
        self.parse_pos = 28
        self.pmus = [None]*self.configFrame.num_pmu
        for i in range(len(self.pmus)):
            self.pmus[i] = PMU(
                self.frame[self.parse_pos:],
                self.configFrame.stations[i]
            )
            self.parse_pos += self.pmus[i].length

    def updateSOC(self):
        """Update SOC."""
        self.soc.ff = self.fracsec / self.configFrame.time_base.baseDecStr
        template = "{:0>4}/{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}{}"
        self.soc.formatted = template.format(
            self.soc.yyyy,
            self.soc.mm,
            self.soc.dd,
            self.soc.hh,
            self.soc.mi,
            self.soc.ss, "{:f}".format(self.soc.ff).lstrip('0')
        )
        dt = datetime(
            self.soc.yyyy,
            self.soc.mm,
            self.soc.dd,
            self.soc.hh,
            self.soc.mi,
            self.soc.ss,
            int(self.soc.ff * 10 ** 6)
        )
        self.soc.utcSec = (dt - datetime(1970, 1, 1)).total_seconds()
        self.parse_pos += 4


class PMU:
    """Class for a PMU in a data frame

    :param pmu_hex_str: Bytes of PMU fields in hex str format
    :type pmu_hex_str: str
    :param station_frame: Station fields from config frame
        describing PMU data
    :type station_frame: Station
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, pmu_hex_str, station_frame, debug=False):

        self.stat = None
        self.phasors = None
        self.freq = None
        self.dfreq = None
        self.analogs = None
        self.digitals = None
        self.length = 0

        self.dbg = debug
        self.stationFrame = station_frame
        self.numOfPhsrs = self.stationFrame.phnmr
        self.fmtOfPhsrs = self.stationFrame.phsrFmt
        self.typeOfPhsrs = self.stationFrame.phsrType
        self.numOfAnlg = self.stationFrame.annmr
        self.numOfDgtl = self.stationFrame.dgnmr
        if self.dbg:
            print("DIG:", self.numOfDgtl)

        self.pmuHex = pmu_hex_str
        if self.dbg:
            print(pmu_hex_str)
        self.parseStat()
        self.parsePhasors()
        self.parseFreq()
        self.parseDfreq()
        self.parseAnalog()
        self.parseDigital()

    def updateLength(self, size_to_add):
        """Keeps track of length for PMU frame only"""
        self.length = self.length + size_to_add

    def parseStat(self):
        """Parse bit mapped flags field"""
        leng = 4
        if self.dbg:
            print("STAT:", self.pmuHex[self.length:self.length+leng])
        self.stat = Stat(self.pmuHex[self.length:self.length+leng])
        self.updateLength(leng)

    def parsePhasors(self):
        """Parse phasor estimates from PMU"""
        if self.dbg:
            print("Phasors")
        self.phasors = [None]*self.numOfPhsrs
        if self.dbg:
            print("NumOfPhsrs:", self.numOfPhsrs)
        for i in range(self.numOfPhsrs):
            self.phasors[i] = Phasor(
                self.pmuHex[self.length:], self.stationFrame,
                self.stationFrame.channels[i]
            )
            if self.dbg:
                print(
                    "PHASOR:",
                    self.pmuHex[self.length:self.length+self.phasors[i].length]
                )
            self.updateLength(self.phasors[i].length)

    def parseFreq(self):
        """Parse frequency"""
        leng = 4 if self.stationFrame.freqType == "INTEGER" else 8
        if self.dbg:
            print("FREQ:", self.pmuHex[self.length:self.length+leng])
        unpack_str = '!h' if leng == 4 else '!f'
        self.freq = struct.unpack(
            unpack_str,
            bytes.fromhex(self.pmuHex[self.length:self.length+leng])
        )[0]
        self.updateLength(leng)
        if self.dbg:
            print("FREQ:", self.freq)

    def parseDfreq(self):
        """Parse rate of change of frequency (ROCOF)"""
        leng = 4 if self.stationFrame.freqType == "INTEGER" else 8
        if self.dbg:
            print("DFREQ: ", self.pmuHex[self.length:self.length+leng])
        unpack_str = '!h' if leng == 4 else '!f'
        self.dfreq = struct.unpack(
            unpack_str,
            bytes.fromhex(self.pmuHex[self.length:self.length+leng])
        )[0]
        self.dfreq = self.dfreq / 100
        self.updateLength(leng)
        if self.dbg:
            print("DFREQ:", self.dfreq)

    def parseAnalog(self):
        """Parse analog data"""
        self.analogs = [None]*self.numOfAnlg
        leng = 4 if self.stationFrame.anlgType == "INTEGER" else 8
        unpack_str = "!h" if leng == 4 else "!f"
        for i in range(self.numOfAnlg):
            name = self.stationFrame.channels[self.numOfPhsrs+i].strip()
            if self.dbg:
                print("ANALOG:",
                      self.pmuHex[self.length:self.length+leng])
            val = struct.unpack(
                unpack_str,
                bytes.fromhex(self.pmuHex[self.length:self.length+leng])
            )[0]
            if self.dbg:
                print(name, "=", val)
            self.analogs[i] = (name, val)
            self.updateLength(leng)

    def parseDigital(self):
        """Parse digital data"""
        self.digitals = [None]*self.numOfDgtl
        leng = 4
        tot_val_bin = hexToBin(self.pmuHex[self.length:self.length+leng], 16)
        for i in range(self.numOfDgtl):
            ind = self.numOfPhsrs + self.numOfAnlg + i
            name = self.stationFrame.channels[ind].strip()
            if self.dbg:
                print("DIGITAL:",
                      self.pmuHex[self.length:self.length+leng])
            val = tot_val_bin[i]
            if self.dbg:
                print(name, "=", val)
            self.digitals[i] = (name, val)
            self.updateLength(leng)


class Phasor:
    """Class for holding phasor information

    :param phsr_val_hex: Phasor values in hex str format
    :type phsr_val_hex: str
    :param station_frame: Station frame which describe data format
    :type station_frame: Station
    :param name: Name of phasor channel
    :type name: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, phsr_val_hex, station_frame, name, debug=False):

        self.phsrFmt = None
        self.phsrType = None
        self.real = None
        self.imag = None
        self.mag = None
        self.deg = None
        self.rad = None
        self.name = None
        self.length = 0

        self.dbg = debug
        self.phsrValHex = phsr_val_hex
        self.stationFrame = station_frame
        self.voltORCurr = self.stationFrame.phunits
        self.name = name

        if self.dbg:
            print("*", name.strip(), "*")

        self.parseFmt()
        self.parseVal()

    def parseFmt(self):
        """Parse format and type of phasor"""
        self.phsrFmt = self.stationFrame.phsrFmt
        self.phsrType = self.stationFrame.phsrType
        self.length = 8 if self.phsrType == "INTEGER" else 16

    def parseVal(self):
        """Parse phasor value"""
        if self.phsrFmt == "RECT":
            self.toRect(self.phsrValHex[:self.length])
        else:
            self.toPolar(self.phsrValHex[:self.length])

    def toRect(self, hex_val):
        """Convert bytes to rectangular values"""
        hex1 = hex_val[:int(self.length/2)]
        hex2 = hex_val[int(self.length/2):]
        unpack_str = "!h" if self.phsrType == "INTEGER" else "!f"
        self.real = struct.unpack(unpack_str, bytes.fromhex(hex1))[0]
        self.imag = struct.unpack(unpack_str, bytes.fromhex(hex2))[0]
        self.mag = math.hypot(self.real, self.imag)
        self.rad = math.atan2(self.imag, self.real)
        self.deg = math.degrees(self.rad)
        if self.dbg:
            print("Real:", hex1, "=", self.real)
            print("Imag:", hex2, "=", self.imag)
            print("Mag:", "=", self.mag)
            print("Rad:", "=", self.rad)
            print("Deg:", "=", self.deg)

    def toPolar(self, hex_val):
        """Convert bytes to polar values"""
        hex1 = hex_val[:int(self.length/2)]
        hex2 = hex_val[int(self.length/2):]
        unpack_str = "!h" if self.phsrType == "INTEGER" else "!f"
        self.mag = struct.unpack(unpack_str, bytes.fromhex(hex1))[0]
        self.rad = struct.unpack(unpack_str, bytes.fromhex(hex2))[0]
        if unpack_str == '!h':
            self.rad = self.rad / 10000
        self.deg = math.degrees(self.rad)
        self.real = self.mag * math.cos(self.deg)
        self.imag = self.mag * math.sin(self.deg)
        if self.dbg:
            print("Real:", hex1, "=", self.real)
            print("Imag:", hex2, "=", self.imag)
            print("Mag:", "=", self.mag)
            print("Rad:", "=", self.rad)
            print("Deg:", "=", self.deg)


class Stat:
    """Class for foling bit mapped flags

    :param stat_hex_str: Stat field in hex string format
    :type stat_hex_str: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, stat_hex_str, debug=False):

        self.dataError = None
        self.pmuSync = None
        self.sorting = None
        self.pmuTrigger = None
        self.configChange = None
        self.dataModified = None
        self.timeQuality = None
        self.unlockedTime = None
        self.triggerReason = None

        self.dbg = debug
        self.statHex = stat_hex_str

        if self.dbg:
            print(stat_hex_str)

        self.parseDataError()
        self.parsePmuSync()
        self.parseSorting()
        self.parsePmuTrigger()
        self.parseConfigChange()
        self.parseDataModified()
        self.parseTimeQuality()
        self.parseUnlockTime()
        self.parseTriggerReason()

    def parseDataError(self):
        """Parse data error bits"""
        self.dataError = DataError(
            int(hexToBin(self.statHex[0], 4)[:2], 2)).name
        if self.dbg:
            print("STAT: ", self.dataError)

    def parsePmuSync(self):
        """Parse PMU sync bit"""
        self.pmuSync = PmuSync(
            int(hexToBin(self.statHex[0], 4)[2], 2)).name
        if self.dbg:
            print("PMUSYNC: ", self.pmuSync)

    def parseSorting(self):
        """Parse data sorting bit"""
        self.sorting = Sorting(
            int(hexToBin(self.statHex[0], 4)[3], 2)).name
        if self.dbg:
            print("SORTING: ", self.sorting)

    def parsePmuTrigger(self):
        """Parse PMU trigger bit"""
        self.pmuTrigger = Trigger(
            int(hexToBin(self.statHex[1], 4)[0], 2)).name
        if self.dbg:
            print("PMUTrigger: ", self.pmuTrigger)

    def parseConfigChange(self):
        """Parse config change bit"""
        self.configChange = ConfigChange(
            int(hexToBin(self.statHex[1], 4)[1], 2)).name
        if self.dbg:
            print("ConfigChange: ", self.configChange)

    def parseDataModified(self):
        """Parse data modified bit"""
        self.dataModified = DataModified(
            int(hexToBin(self.statHex[1], 4)[2], 2)).name
        if self.dbg:
            print("DataModified: ", self.dataModified)

    def parseTimeQuality(self):
        """Parse time quality bits"""
        self.unlockedTime = TimeQuality(
            int(hexToBin(self.statHex[1:3], 8)[3:6], 2)).name
        if self.dbg:
            print("TimeQuality: ", self.unlockedTime)

    def parseUnlockTime(self):
        """Parse unlocked time bits"""
        self.unlockedTime = UnlockedTime(
            int(hexToBin(self.statHex[2], 4)[2:], 2)).name
        if self.dbg:
            print("UnlockTime: ", self.unlockedTime)

    def parseTriggerReason(self):
        """Parse trigger reason bits"""
        self.triggerReason = TriggerReason(
            int(hexToBin(self.statHex[3], 4), 2)).name
        if self.dbg:
            print("TriggerReason: ", self.triggerReason)
