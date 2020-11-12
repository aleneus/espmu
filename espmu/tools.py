"""Tools for common functions relayed to commanding, reading, and
parsing PMU data."""

from espmu.client import Client
from espmu.pmuConfigFrame import ConfigFrame
from espmu.pmuCommandFrame import CommandFrame
from espmu.pmuLib import bytesToHexStr
from espmu.pmuDataFrame import DataFrame

MAXFRAMESIZE = 65535


def turnDataOff(cli, idcode):
    """
    Send command to turn off real-time data

    :param cli: Client being used to connect to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmd_off = CommandFrame("DATAOFF", idcode)
    cli.sendData(cmd_off.fullFrameBytes)


def turnDataOn(cli, idcode):
    """
    Send command to turn on real-time data

    :param cli: Client connection to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmd_on = CommandFrame("DATAON", idcode)
    cli.sendData(cmd_on.fullFrameBytes)


def requestConfigFrame2(cli, idcode):
    """
    Send command to request config frame 2

    :param cli: Client connection to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmd_config_2 = CommandFrame("CONFIG2", idcode)
    cli.sendData(cmd_config_2.fullFrameBytes)


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

    full_hex_str = ""
    if type(rcvr) == "client":
        intro_hex_str = bytesToHexStr(rcvr.readSample(4))
        len_to_read = int(intro_hex_str[5:], 16)
        rest_hex_str = bytesToHexStr(rcvr.readSample(len_to_read))
        full_hex_str = intro_hex_str + rest_hex_str
    else:
        full_hex_str = bytesToHexStr(rcvr.readSample(64000))

    return full_hex_str


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


def startDataCapture(idcode, ip, port=4712, proto="TCP", debug=False):
    """
    Connect to data source, request config frame, send data start command

    :param idcode: Frame ID of PMU
    :type idcode: int
    :param ip: IP address of data source
    :type ip: str
    :param port: Command port on data source
    :type port: int
    :param proto: Use TCP or UDP
    :type proto: str
    :param debug: Print debug statements
    :type debug: bool

    :return: Populated :py:class:`espmu.pmuConfigFrame.ConfigFrame` object
    """
    config_frame = None

    cli = Client(ip, port, proto)
    cli.setTimeout(5)
    turnDataOff(cli, idcode)
    while config_frame is None:
        requestConfigFrame2(cli, idcode)
        config_frame = readConfigFrame2(cli, debug)
    cli.stop()

    return config_frame


def getStations(config_frame):
    """
    Returns all station names from the config frame

    :param config_frame: ConfigFrame containing stations
    :type config_frame: ConfigFrame

    :return: List containing all the station names
    """

    return config_frame.stations


def parseSamples(data, config_frame, pmus):
    """
    Takes in an array of dataFrames and inserts the data into an array
    of aggregate phasors

    :param data: List containing all the data samples
    :type data: List
    :param config_frame: ConfigFrame containing stations
    :type config_frame: ConfigFrame
    :param pmus: List of phasor values
    :type pmus: List

    :return: List containing all the phasor values
    """
    num_of_samples = len(data)
    for s in range(num_of_samples):
        for p in range(len(data[s].pmus)):
            for phasor in range(len(data[s].pmus[p].phasors)):
                msec = (data[s].fracsec / config_frame.time_base.baseDecStr)
                utc_timestamp = data[s].soc.utcSec + msec
                pmus[p][phasor].addSample(
                    utc_timestamp,
                    data[s].pmus[p].phasors[phasor].mag,
                    data[s].pmus[p].phasors[phasor].rad)

    return pmus
