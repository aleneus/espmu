"""In this module the frame for transfer data is implemented."""

from struct import pack
from PyCRC.CRCCCITT import CRCCCITT
from espmu.pmuLib import intToHexStr, doubleToHexStr


class TransferFrame():
    """
    Custom class meant to create a message that can be passed to a
    socket connection. Only contains timestamp, phasor values, and ID
    for each phasor

    :param inputDataFrame: Populated data frame containing measurement values
    :type inputDataFrame: pmuDataFrame
    """

    def __init__(self, inputDataFrame):
        self.header = "AAFF"
        self.length = 0
        self.timestamp = None
        self.numOfPhasors = 0
        self.phasors = []
        self.crc = None
        self.fullFrameBytes = ""
        self.fullFrameHexStr = ""

        self.dataFrame = inputDataFrame
        self.parseDataSample()
        self.createFullFrame()

    def parseDataSample(self):
        """Parse the input data sample"""
        self.length += len(self.header) / 2  # Separator
        tmp = self.dataFrame.fracsec
        tmp = tmp / self.dataFrame.configFrame.time_base.baseDecStr
        tmp += self.dataFrame.soc.utcSec
        self.timestamp = tmp
        self.parsePhasors()

        self.length += len(pack('d', self.timestamp))  # Double
        self.length += len(pack('H', self.numOfPhasors))  # Unsigned Short
        self.length += len(pack('I', int(self.length)))   # Unsigned Int

    def parsePhasors(self):
        """Parse the phasors in the data sample to extract measurements"""
        ident = 0
        for p in range(self.dataFrame.configFrame.num_pmu):
            for ph in range(self.dataFrame.pmus[p].numOfPhsrs):
                frm = self.dataFrame.configFrame
                units = frm.stations[p].phunits[ph].voltORcurr
                field = PhasorField(
                    self.dataFrame.pmus[p].phasors[ph],
                    ident, units
                )
                self.length += len(field.fullFrameHexStr)/2
                self.phasors.append(field)
                ident = ident + 1
        self.numOfPhasors = len(self.phasors)

    def genCrc(self):
        """Generate CRC-CCITT"""
        crc_calc = CRCCCITT('FFFF')
        frame_in_bytes = bytes.fromhex(self.fullFrameHexStr)
        the_crc = hex(crc_calc.calculate(frame_in_bytes))[2:].zfill(4)
        self.crc = the_crc.upper()

    def createFullFrame(self):
        """Put all the pieces to together to create full transfer frame"""
        self.fullFrameHexStr += self.header +\
            intToHexStr(int(self.length)).zfill(8).upper() +\
            doubleToHexStr(self.timestamp).zfill(16).upper() +\
            intToHexStr(self.numOfPhasors).zfill(4).upper()
        for ph in self.phasors:
            self.fullFrameHexStr += ph.fullFrameHexStr
            # Removed CRC because it was slowing down transfer rates
        # self.genCrc()
        # self.fullFrameHexStr += self.crc
        self.fullFrameBytes = bytes.fromhex(self.fullFrameHexStr)


class PhasorField():
    """Class to hold simplified phasor fields

    :param phasor: Phasor containing measurements
    :type phasor: Phasor
    :param idNum: Frame ID to use
    :type idNum: int
    :param theUnits:  Volts or Amps
    :type theUnits: str
    """

    def __init__(self, phasor, idNum, theUnits):
        self.options = None
        self.fullFrameHexStr = None
        self.length = 0

        self.phasorFrame = phasor
        self.ident = idNum
        self.value = self.phasorFrame.mag
        self.angle = self.phasorFrame.rad
        self.units = theUnits
        self.parseOptions()
        self.createPhasorFieldFrame()

    def parseOptions(self):
        """Parse options and create bytes as hex str"""
        if self.units == "VOLTAGE":
            self.options = intToHexStr(0).zfill(4)
        else:
            self.options = intToHexStr(2 ** 15)

    def createPhasorFieldFrame(self):
        """Create phasor field frame inside full transfer frame"""
        full_frame_hex_str = ""
        full_frame_hex_str += intToHexStr(self.ident).zfill(4)
        full_frame_hex_str += doubleToHexStr(self.value)
        full_frame_hex_str += doubleToHexStr(self.angle)
        full_frame_hex_str += self.options
        self.fullFrameHexStr = full_frame_hex_str.upper()
        self.length = int(len(full_frame_hex_str)/2)
