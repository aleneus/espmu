"""Tools for common functions relayed to commanding, reading, and
parsing PMU data."""

from .client import Client
from .pmuConfigFrame import ConfigFrame
from .pmuCommandFrame import CommandFrame
from .pmuLib import bytesToHexStr
from .pmuDataFrame import DataFrame

MAXFRAMESIZE = 65535


def turnDataOff(cli, idcode):
    """
    Send command to turn off real-time data

    :param cli: Client being used to connect to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmdOff = CommandFrame("DATAOFF", idcode)
    cli.sendData(cmdOff.fullFrameBytes)


def turnDataOn(cli, idcode):
    """
    Send command to turn on real-time data

    :param cli: Client connection to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmdOn = CommandFrame("DATAON", idcode)
    cli.sendData(cmdOn.fullFrameBytes)


def requestConfigFrame2(cli, idcode):
    """
    Send command to request config frame 2

    :param cli: Client connection to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmdConfig2 = CommandFrame("CONFIG2", idcode)
    cli.sendData(cmdConfig2.fullFrameBytes)


def readConfigFrame2(cli, debug=False):
    """
    Retrieve and return config frame 2 from PMU or PDC

    :param cli: Client connection to data source
    :type cli: Client
    :param debug: Print debug statements
    :type debug: bool
    :return: Fasle (no answer at all), None (answer is wrong) or
        Populated ConfigFrame (answer is ok)

    """
    leading_byte = cli.readSample(1)
    if leading_byte == "":  # can't get sample at all
        return False
    if leading_byte[0] != 170:  # wrong synchronization word
        return None
    sample = leading_byte + cli.readSample(3)
    if (sample[1] & 112) != 48:  # wrong frame type
        return None
    config_frame = ConfigFrame(bytesToHexStr(sample), debug)
    exp_size = config_frame.framesize
    sample = cli.readSample(exp_size - 4)
    config_frame.frame = config_frame.frame + bytesToHexStr(sample).upper()
    config_frame.finishParsing()
    return config_frame


def getDataSample(rcvr):
    """
    Get a data sample regardless of TCP or UDP connection

    :param rcvr: Object used for receiving data frames
    :type rcvr: :class:`Client`/:class:`Server`
    :return: Data frame in hex string format
    """
    fullHexStr = ""
    if type(rcvr) == "client":
        introHexStr = bytesToHexStr(rcvr.readSample(4))
        lenToRead = int(introHexStr[5:], 16)
        remainingHexStr = bytesToHexStr(rcvr.readSample(lenToRead))
        fullHexStr = introHexStr + remainingHexStr
    else:
        fullHexStr = bytesToHexStr(rcvr.readSample(64000))
    return fullHexStr


def get_data_frames(data_sample, conf_frame):
    """ Return list of data frames from data_sample. """
    data_frames = []
    start_pos = 0
    while True:
        tail = data_sample[start_pos:]
        data_frame = DataFrame(tail, conf_frame)
        data_frames.append(data_frame)
        start_pos += data_frame.parse_pos
        if start_pos >= len(data_sample):
            break
    return data_frames


def startDataCapture(idcode, ip, port=4712, tcpUdp="TCP", debug=False):
    """
    Connect to data source, request config frame, send data start command

    :param idcode: Frame ID of PMU
    :type idcode: int
    :param ip: IP address of data source
    :type ip: str
    :param port: Command port on data source
    :type port: int
    :param tcpUdp: Use TCP or UDP
    :type tcpUdp: str
    :param debug: Print debug statements
    :type debug: bool

    :return: Populated :py:class:`espmu.pmuConfigFrame.ConfigFrame` object
    """
    configFrame = None

    cli = Client(ip, port, tcpUdp)
    cli.setTimeout(5)
    turnDataOff(cli, idcode)
    while configFrame is None:
        requestConfigFrame2(cli, idcode)
        configFrame = readConfigFrame2(cli, debug)
    cli.stop()

    return configFrame


def getStations(configFrame):
    """
    Returns all station names from the config frame

    :param configFrame: ConfigFrame containing stations
    :type configFrame: ConfigFrame

    :return: List containing all the station names
    """
    stations = []
    for s in configFrame.stations:
        # print("Station:", s.stn)
        stations.append(s)
    return stations


def parseSamples(data, configFrame, pmus):
    """
    Takes in an array of dataFrames and inserts the data into an array
    of aggregate phasors

    :param data: List containing all the data samples
    :type data: List
    :param configFrame: ConfigFrame containing stations
    :type configFrame: ConfigFrame
    :param pmus: List of phasor values
    :type pmus: List

    :return: List containing all the phasor values
    """
    numOfSamples = len(data)
    for s in range(0, numOfSamples):
        for p in range(0, len(data[s].pmus)):
            for phasor in range(0, len(data[s].pmus[p].phasors)):
                msec = (data[s].fracsec / configFrame.time_base.baseDecStr)
                utc_timestamp = data[s].soc.utcSec + msec
                pmus[p][phasor].addSample(
                    utc_timestamp,
                    data[s].pmus[p].phasors[phasor].mag,
                    data[s].pmus[p].phasors[phasor].rad)

    return pmus
