"""Implementation of client."""

import socket


class Client:
    """
    Client class that creates a client and provides simple functions
    for connecting to PMUs or PDCs without needing to directly use
    Python's socket library.  Supports INET and UNIX sockets

    :param theDestIp: IP address to connect to.  If using unix socket
        this is the file name to connect to
    :type theDestIp: str

    :param theDestPort: Port to connect to
    :type theDestPort: int

    :param proto: Protocol to use.  Accepts TCP or UDP
    :type proto: str

    :param sockType: Type of socket to create.  INET or UNIX
    :type sockType: str

    """
    def __init__(self, theDestIp, theDestPort, proto="TCP", sockType="INET"):

        self.srcIp = None
        self.srcPort = None
        self.destAddr = None
        self.srcAddr = None
        self.theSocket = None
        self.theConnection = None
        self.useUdp = False
        self.unixSock = False

        self.destIp = theDestIp
        self.destPort = theDestPort
        self.destAddr = (theDestIp, theDestPort)
        if proto.upper() == "UDP":
            self.useUdp = True
        if sockType.upper() == "UNIX":
            self.unixSock = True

        self.createSocket()
        # self.connectToDest()

    def createSocket(self):
        """Create socket based on constructor arguments"""
        if self.useUdp:
            if self.unixSock:
                self.theSocket = socket.socket(
                    socket.AF_UNIX, socket.SOCK_DGRAM)
            else:
                self.theSocket = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM)
        else:
            if self.unixSock:
                self.theSocket = socket.socket(
                    socket.AF_UNIX, socket.SOCK_STREAM)
            else:
                self.theSocket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)

    def connectToDest(self):
        """Connect socket to destination IP:Port.  If UNIX socket then
        use destIP."""
        try:
            if not self.useUdp:
                if self.unixSock:
                    self.theSocket.connect(self.destIp)
                else:
                    self.theSocket.connect(self.destAddr)
            return True
        except OSError:
            return False

    def readSample(self, bytes_to_read):
        """
        Read a sample from the socket

        :param bytes_to_read: Number of bytes to read from socket
        :type bytes_to_read: int

        :return: Byte array of data read from socket
        """
        try:
            if self.useUdp:
                return self.theSocket.recvfrom(bytes_to_read)
            return self.theSocket.recv(bytes_to_read)
        except socket.timeout:
            print("Socket Timeout")
            return ""

    def sendData(self, bytes_to_send):
        """Send bytes to destination

        :param bytes_to_send: Number of bytes to send
        :type bytes_to_send: int
        """
        if self.useUdp:
            if self.unixSock:
                self.theSocket.sendto(bytes_to_send, self.destIp)
            else:
                self.theSocket.sendto(bytes_to_send, self.destAddr)
        else:
            self.theSocket.send(bytes_to_send)

    def stop(self):
        """Close the socket connection"""
        self.theSocket.close()

    def setTimeout(self, secs_num):
        """Set socket timeout

        :param secs_num: Time to wait for socket action to complete
            before throwing timeout exception
        :type secs_num: int
        """
        self.theSocket.settimeout(secs_num)

    def __class__(self):
        return "client"
