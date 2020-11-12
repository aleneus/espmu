"""In this module the base class for frames is defined."""
from datetime import datetime
from espmu.pmuEnum import FrameType
from espmu.pmuLib import hexToBin


class PMUFrame:
    """
    Super class for all C37.118-2005/C37.118-2011 frames

    :param frame_in_hex_str: Bytes from frame (any time) in hex str format
    :type strameInHexStr: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, frame_in_hex_str, debug=False):
        """
        PMUFrame constructor

        :param frame_in_hex_str: Hex representation of frame bytes
        :type frame_in_hex_str: str
        :param debug: Print debug statements or not
        :type debug: bool
        """

        self.length = 0

        self.dbg = debug
        self.frame = frame_in_hex_str.upper()
        self.parseSYNC()
        self.parseFRAMESIZE()

        self.idcode = None
        self.soc = None
        self.tq = None
        self.fracsec = None
        self.chk = None

    def finishParsing(self):
        """
        When getting the config frame, the size is unknown.  After
        creating a PMUFrame with the first 4 bytes, the remaining
        frame bytes are read and added to self.frame. Once that is
        populated the remaining fields can be parsed.

        """
        self.parseIDCODE()
        self.parseSOC()
        self.parseTQ()
        self.parseFRACSEC()
        self.parseCHK()

    def parseSYNC(self):
        """Parse frame synchronization word"""
        self.sync = SYNC(self.frame[:4])
        self.updateLength(4)

    def parseFRAMESIZE(self):
        """Parse frame size"""
        framesize_size = 4
        self.framesize = int(
            self.frame[self.length:self.length+framesize_size],
            16
        )
        self.updateLength(framesize_size)

        if self.dbg:
            print("FRAMESIZE: ", self.framesize)

    def parseIDCODE(self):
        """Parse data stream ID number"""
        idcode_size = 4
        self.idcode = int(self.frame[self.length:self.length+idcode_size], 16)
        self.updateLength(idcode_size)

        if self.dbg:
            print("IDCODE: ", self.idcode)

    def parseSOC(self):
        """Parse second-of-century timestamp"""
        soc_size = 8
        self.soc = SOC(self.frame[self.length:self.length+soc_size])
        self.updateLength(soc_size)

    def parseTQ(self):
        """Parse time guality flag"""
        tq_size = 2
        self.tq = int(self.frame[self.length:self.length+tq_size], 16)
        self.updateLength(tq_size)

        if self.dbg:
            print("TQ: ", self.tq)

    def parseFRACSEC(self):
        """Parse fraction of second and time quality word"""
        fracsec_size = 6
        self.fracsec = int(
            self.frame[self.length:self.length+fracsec_size], 16)
        self.updateLength(fracsec_size)

        if self.dbg:
            print("FRACSEC: ", self.fracsec)

    def parseCHK(self):
        """Parse CRC-CCITT word"""
        chk_size = 4
        self.chk = self.frame[-chk_size:]

        if self.dbg:
            print("CHK: ", self.chk)

    def updateLength(self, size_to_add):
        """Keeps track of index for overall frame"""
        self.length = self.length + size_to_add


class SYNC:
    """Class for describing the frame synchronization word

    :param sync_hex_str: Sync byte array in hex str format
    :type sync_hex_str: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, sync_hex_str, debug=False):
        self.dbg = debug
        self.syncHex = sync_hex_str
        self.parseType()
        self.parseVers()

        self.frameType = None
        self.frameVers = None

    def parseType(self):
        """Parse frame type"""
        type_bin_str = hexToBin(self.syncHex[2], 3)
        type_num = int(type_bin_str, 2)
        self.frameType = FrameType(type_num).name

        if self.dbg:
            print("Type: ", self.frameType)

    def parseVers(self):
        """Parse frame version"""
        vers_bin_str = hexToBin(self.syncHex[3], 4)
        self.frameVers = int(vers_bin_str, 2)

        if self.dbg:
            print("Vers: ", self.frameVers)


class SOC:
    """Class for second-of-century (SOC) word (32 bit unsigned)

    :param soc_hex_str: Second-of-century byte array in hex str format
    :type soc_hex_str: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, soc_hex_str, debug=False):
        self.dbg = debug
        self.socHex = soc_hex_str
        self.secCount = int(soc_hex_str, 16)
        self.parseSecCount()
        if self.dbg:
            print("SOC: ", self.secCount, " - ", self.formatted)

    def parseSecCount(self):
        """Parse SOC into UTC timestamp and pretty formatted timestamp"""
        parsed_date = datetime.fromtimestamp(self.secCount)
        self.yyyy = parsed_date.year
        self.mm = parsed_date.month
        self.dd = parsed_date.day
        self.hh = parsed_date.hour
        self.mi = parsed_date.minute
        self.ss = parsed_date.second
        self.ff = 0
        self.formatted = "{:0>4}/{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}".format(
            self.yyyy, self.mm, self.dd, self.hh, self.mi, self.ss
        )
        dt = datetime(self.yyyy, self.mm, self.dd, self.hh, self.mi, self.ss)
        self.utcSec = (dt - datetime(1970, 1, 1)).total_seconds()
