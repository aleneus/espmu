"""Class for parsing Config Frame 1 or 2."""

from espmu.pmuEnum import (NumType, PhsrFmt, FundFreq,
                           MeasurementType, AnlgMsrmnt)
from espmu.pmuLib import hexToBin
from espmu.pmuFrame import PMUFrame


class ConfigFrame(PMUFrame):
    """Parses Config Frame (1 or 2)

    :param frameInHexStr: Config frame as byte array in hex str format
    :type frameInHexStr: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def finishParsing(self):
        """After first 4 bytes are received, the client reads the
        remaining config frame bytes.  This function parses those
        remaining bytes"""
        super().finishParsing()
        self.parseTIME_BASE()
        self.parseNUM_PMU()
        self.parseStations()
        self.parseDATARATE()

    def parseTIME_BASE(self):
        """Parses resolution of FRACSEC"""
        timebaseSize = 8
        self.time_base = TimeBase(
            self.frame[self.length:self.length+timebaseSize])
        self.updateLength(timebaseSize)
        if self.dbg:
            print("TIME_BASE: ",
                  self.time_base.baseDecStr, sep="")

    def parseNUM_PMU(self):
        """Parse number of PMUs sending data"""
        numpmuSize = 4
        self.num_pmu = int(self.frame[self.length:self.length+numpmuSize], 16)
        self.updateLength(numpmuSize)
        if self.dbg:
            print("NUM_PMU: ", self.num_pmu, sep="")

    def parseStations(self):
        """Parse station names for each PMU"""
        self.stations = [None]*self.num_pmu
        for i in range(0, self.num_pmu):
            self.stations[i] = Station(self.frame[self.length:])
            self.updateLength(self.stations[i].length)
            if self.dbg:
                print("***** Station ",
                      (i+1), " *****", sep="")

    def parseDATARATE(self):
        """Parse data rate at which data will be received"""
        datarateSize = 4
        self.datarate = int(
            self.frame[self.length:self.length+datarateSize], 16)
        self.updateLength(datarateSize)
        if self.dbg:
            print("DATARATE: ", self.datarate)


class TimeBase:
    """Class for parsing the TIME_BASE word"""

    def __init__(self, timeBaseHexStr, debug=False):
        self.dbg = debug
        self.timeBaseHex = timeBaseHexStr
        self.flagsBinStr = hexToBin(timeBaseHexStr, 32)[:8]
        # Not parsed anywhere because so far they aren't being used
        self.baseDecStr = int(timeBaseHexStr[1:], 16)


class Station:
    """Class for parsing station information including all PMU
    information.  Fields 8-19

    :param theStationHex: Station fields in hex str format
    :type theStationHex: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, theStationHex, debug=False):

        self.stn = None
        self.idcode_data = None
        self.fmt = None
        self.freqType = None
        self.anlgType = None
        self.phsrType = None
        self.phsrFmt = None
        self.phnmr = None
        self.annmr = None
        self.dgnmr = None
        self.ph_channels = None
        self.an_channels = None
        self.dg_channels = None
        self.channels = None
        self.numOfChns = 0
        self.phunits = None
        self.anunits = None
        self.digunits = None
        self.fnom = None
        self.cfgcnt = None
        self.length = 0

        self.dbg = debug
        self.stationFrame = theStationHex
        self.parseSTN()
        self.parseIDCODE_data()
        self.parseFORMAT()
        self.parsePHNMR()
        self.parseANNMR()
        self.parseDGNMR()
        self.parseCHNAME()
        self.parsePHUNIT()
        self.parseANUNIT()
        self.parseDIGUNIT()
        self.parseFNOM()
        self.parseCFGCNT()

    def updateLength(self, sizeToAdd):
        """Updates length of station frames only

        :param sizeToAdd: Number of bytes to add to frame length
        :type sizeToAdd: int
        """
        self.length = self.length + sizeToAdd

    def parseSTN(self):
        """Parses station name field"""
        leng = 32
        self.stn = bytes.fromhex(
            self.stationFrame[self.length:self.length+leng]).decode('ascii')
        self.updateLength(leng)
        if self.dbg:
            print("STN: ", self.stn, sep="")

    def parseIDCODE_data(self):
        """Parses station ID code field"""
        leng = 4
        self.idcode_data = int(
            self.stationFrame[self.length:self.length+leng], 16)
        self.updateLength(leng)
        if self.dbg:
            print("IDCODE_data: ", self.idcode_data)

    def parseFORMAT(self):
        """Parses data format field"""
        leng = 4
        fmts = hexToBin(
            self.stationFrame[self.length:self.length+leng], 32)[-4:]

        self.freqType = NumType(int(fmts[0], 2)).name
        self.anlgType = NumType(int(fmts[1], 2)).name
        self.phsrType = NumType(int(fmts[2], 2)).name
        self.phsrFmt = PhsrFmt(int(fmts[3], 2)).name

        self.updateLength(leng)

        if self.dbg:
            print("FreqFmt: ", self.freqType)
            print("AnlgFmt: ", self.anlgType)
            print("PhsrFmt: ", self.phsrType)
            print("PhsrFmt: ", self.phsrFmt)

    def parsePHNMR(self):
        """Parses number of phasors field"""
        leng = 4
        self.phnmr = int(self.stationFrame[self.length:self.length+leng], 16)
        self.updateLength(leng)
        if self.dbg:
            print("PHNMR: ", self.phnmr, sep="")

    def parseANNMR(self):
        """Parses number of analog values field"""
        leng = 4
        self.annmr = int(
            self.stationFrame[self.length:self.length+leng], 16)
        self.updateLength(leng)
        if self.dbg:
            print("ANNMR: ", self.annmr, sep="")

    def parseDGNMR(self):
        """Parses number of digital values field"""
        leng = 4
        self.dgnmr = int(
            self.stationFrame[self.length:self.length+leng], 16)
        self.updateLength(leng)
        if self.dbg:
            print("DGNMR: ", self.dgnmr, sep="")

    def parsePHNAME(self):
        """Parses phasor field"""
        self.numOfChns = self.phnmr
        self.ph_channels = [None]*self.numOfChns
        leng = 32
        for i in range(0, self.numOfChns):
            self.ph_channels[i] = bytes.fromhex(
                self.stationFrame[self.length:self.length+leng]
            ).decode('ascii')
            self.updateLength(leng)
            if self.dbg:
                print(self.ph_channels[i])

    def parseANNAME(self):
        """Parses analog channel names field"""
        self.numOfChns = self.annmr
        self.an_channels = [None]*self.numOfChns
        leng = 32
        for i in range(0, self.numOfChns):
            self.an_channels[i] = bytes.fromhex(
                self.stationFrame[self.length:self.length+leng]
            ).decode('ascii')
            self.updateLength(leng)
            if self.dbg:
                print(self.an_channels[i])

    def parseDGNAME(self):
        """Parses digital channel names field"""
        self.numOfChns = 16 * self.dgnmr
        self.dg_channels = [None]*self.numOfChns
        leng = 32
        for i in range(0, self.numOfChns):
            self.dg_channels[i] = bytes.fromhex(
                self.stationFrame[self.length:self.length+leng]
            ).decode('ascii')
            self.updateLength(leng)
            if self.dbg:
                print(self.dg_channels[i])

    def parseCHNAME(self):
        """Parses phasor and channel names field"""
        self.parsePHNAME()
        self.parseANNAME()
        self.parseDGNAME()
        self.channels = self.ph_channels + self.an_channels + self.dg_channels

    def parsePHUNIT(self):
        """Parse conversion factor for phasor channels"""
        self.phunits = [None]*self.phnmr
        leng = 8
        for i in range(0, self.phnmr):
            self.phunits[i] = Phunit(
                self.stationFrame[self.length:self.length+leng])
            self.updateLength(leng)

    def parseANUNIT(self):
        """Parse conversion factor for analog channels"""
        self.anunits = [None]*self.annmr
        leng = 8
        for i in range(0, self.annmr):
            self.anunits[i] = Anunit(
                self.stationFrame[self.length:self.length+leng])
            self.updateLength(leng)

    def parseDIGUNIT(self):
        """Parse mask words for digital status words"""
        self.digunits = [None]*self.dgnmr
        leng = 8
        for i in range(0, self.dgnmr):
            self.digunits[i] = Digunit(
                self.stationFrame[self.length:self.length+leng])
            self.updateLength(leng)

    def parseFNOM(self):
        """Nominal line frequency code and flags"""
        leng = 4
        hexDigit = self.stationFrame[self.length+4]
        hexDigitLSB = hexToBin(hexDigit, 8)[7]
        hexDigitDec = int(hexDigitLSB, 2)

        self.fnom = FundFreq(hexDigitDec).name
        self.updateLength(leng)
        if self.dbg:
            print("FNOM: ", self.fnom)

    def parseCFGCNT(self):
        """Parse configuration change count"""
        leng = 4
        self.cfgcnt = int(
            self.stationFrame[self.length:self.length+leng], 16)
        self.updateLength(leng)
        if self.dbg:
            print("CFGCNT: ", self.cfgcnt)


class Phunit:
    """Class for conversion factor for phasor channels

    :param phunitHexStr: Conversion factor field in hex str format
    :type phunitHexStr: str
    """

    def __init__(self, phunitHexStr, debug=False):
        self.voltORcurr = None
        self.value = None

        self.dbg = debug
        self.phunitHex = phunitHexStr
        self.parseVoltOrCurr()
        self.parseValue()
        if self.dbg:
            print("PHUNIT: ",
                  self.voltORcurr, " - ", self.value, sep="")

    def parseVoltOrCurr(self):
        """Determine if measurement type is voltage or current"""
        self.voltORcurr = MeasurementType(int(self.phunitHex[0:2], 16)).name

    def parseValue(self):
        """Parse value of conversion factor"""
        self.value = int(self.phunitHex[2:], 16)


class Anunit:
    """Class for conversion factor for analog channels

    :param anunitHexStr: Conversion factor for analog channels field
        in hex str format
    :type anunitHexStr: str
    """
    def __init__(self, anunitHexStr, debug=False):

        self.anlgMsrmnt = None
        self.userDefinedScale = None

        self.dbg = debug
        self.anunitHex = anunitHexStr
        self.parseAnlgMsrmnt()
        self.parseUserDefinedScale()
        if self.dbg:
            print("ANUNIT: ",
                  self.anlgMsrmnt, " - ",
                  self.userDefinedScale, sep="")

    def parseAnlgMsrmnt(self):
        """Parse analog measurement type"""
        self.anlgMsrmnt = AnlgMsrmnt(int(self.anunitHex[0:2], 16)).name

    def parseUserDefinedScale(self):
        """Parse user defined scaling"""
        self.userDefiend = self.anunitHex[1:]


class Digunit:
    """Class for mask of digital status words

    :param digunitHexStr: Conversion factor for digital status
        channels field in hex str format
    :type digunitHexStr: str
    """

    def __init__(self, digunitHexStr, debug=False):
        self.dbg = debug
        self.digunitHex = digunitHexStr
        if self.dbg:
            print("DIGUNIT: ", self.digunitHex)
