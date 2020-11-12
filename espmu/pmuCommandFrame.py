"""Command frame."""
from time import time
from datetime import datetime
from PyCRC.CRCCCITT import CRCCCITT
from espmu.pmuFrame import PMUFrame
from espmu.pmuEnum import Command


class CommandFrame(PMUFrame):
    """
    Class for creating a Command Frame based on C37.118-2005

    :param command_str: Command to send
    :type command_str: str
    :param pmu_id: Frame ID of PMU
    :type pmu_id: int
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, command_str, pmu_id, debug=False):

        # Monitored as fields are added then inserted back into
        # command frame before doing CRC
        self.length = 0

        self.dbg = debug
        self.command = Command[command_str.upper()]
        self.pmuId = hex(pmu_id)
        self.createCommand()

        self.chk = None

    def createCommand(self):
        """Create each field based on the command to send and the frame ID"""

        # Command frame sync bytes
        self.sync = self.genSync()
        self.idcode = self.genIdcode()
        self.soc = self.genSoc()
        self.fracsec = self.genFracsec()
        self.commandHex = self.genCmd()
        self.framesize = hex(int((self.length+8)/2))[2:].zfill(4)

        cmd_hex = self.sync
        cmd_hex += self.framesize
        cmd_hex += self.idcode
        cmd_hex += self.soc
        cmd_hex += self.fracsec
        cmd_hex += self.commandHex

        self.genChk(cmd_hex)
        cmd_hex = cmd_hex + self.chk
        self.fullFrameHexStr = cmd_hex.upper()
        self.fullFrameBytes = bytes.fromhex(self.fullFrameHexStr)

    # # # # # #
    # Methods follow fields in Command Frame.
    # Return Hex str for easy debugging
    # # # # # #
    def genSync(self):
        """:return: Sync field bytes as hex str"""
        self.updateLength(4)
        return "AA41"

    def genIdcode(self):
        """:return: ID code field bytes as hex str"""
        self.updateLength(4)
        return self.pmuId[2:].zfill(4).upper()

    def genSoc(self):
        """Generate second of century based on current time

        :return: SOC field bytes as hex str
        """
        self.updateLength(8)
        hex_val = hex(int(round(time()))).upper()[2:].zfill(4)
        return hex_val.upper()

    def genFracsec(self):
        """Generate fraction of seconds based on current time

        :return: FRACSEC field bytes as hex str
        """
        self.updateLength(8)
        now = datetime.now()
        hex_val = hex(now.microsecond)[2:].zfill(8)
        return hex_val.upper()

    def genCmd(self):
        """Generate command as hex str

        :return: Command field bytes as hex str
        """
        self.updateLength(4)
        cmd_hex = hex(
            int(bin(self.command.value)[2:].zfill(16), 2))[2:].zfill(4)
        return cmd_hex.upper()

    def genChk(self, crc_input_data):
        """Generate CRC-CCITT based on command frame"""
        crc_calc = CRCCCITT('FFFF')
        frame_in_bytes = bytes.fromhex(crc_input_data)
        the_crc = hex(crc_calc.calculate(frame_in_bytes))[2:].zfill(4)
        self.chk = the_crc.upper()
