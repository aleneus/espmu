"""Server implementation."""
import socket


class Server:
    """
    Server class that creates a server and provides simple functions
    for incoming connections/data from PMUs or PDCs without needing to
    directly use Python's socket library.  Supports INET sockets only
    (will eventually be updated).

    :param the_port: Local port to listen on
    :type the_port: int
    :param proto: Protocol to use.  Accepts TCP or UDP
    :type proto: str
    :param print_info: Specifies whether or not to print debug statements
    :type print_info: bool
    """

    def __init__(self, the_port, proto="TCP", print_info=False):

        self.serverIP = None
        self.socketConn = None
        self.connection = None
        self.clientAddr = None
        self.serverAddr = ""
        self.__print_info = print_info

        self.serverPort = the_port
        self.serverAddr = (self.serverAddr, self.serverPort)

        if proto.lower() == "udp":
            self.useUdp = True
        else:
            self.useUdp = False

        self.startServer(5)
        self.waitForConnection()

    def startServer(self, queue_len):
        """Starts the python server and listens for connections

        :param queue_len: Max number of queued connections.  Usually
            defaults to 5
        :type queue_len: int
        """

        if self.useUdp:
            self.socketConn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.__info("Starting UDP Server on", self.serverAddr)
            self.socketConn.bind(self.serverAddr)
        else:
            self.socketConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.__print_info:
                print("Starting TCP Server on", self.serverAddr)
            self.socketConn.bind(self.serverAddr)
            self.socketConn.listen(queue_len)

    def waitForConnection(self):
        """Will block program execution until a connection is achieved"""
        self.__info("**********")

        if self.useUdp:
            return

        self.__info("Waiting for connection...")

        self.connection, self.clientAddr = self.socketConn.accept()

    def readSample(self, length):
        """Will read exactly exactly as many bytes as specified by
        length and return them as an int"""
        data = ""
        if self.useUdp:
            data = self.socketConn.recvfrom(length)[0]
        else:
            if self.connection is None:
                self.waitForConnection()
            data = self.connection.recv(length)

        if not data:
            self.__info("Invalid/No Data Received")

        return data

    def stop(self):
        """Closes server connections"""
        self.__info("\n**********")

        if self.useUdp:
            self.socketConn.close()
        else:
            if self.__print_info:
                print("Stopping server...")

        self.__info("Stopping", self.serverAddr)

    def setTimeout(self, secs_num):
        """Set socket timeout

        :param secs_num: Time to wait for socket action to complete
            before throwing timeout exception
        :type secs_num: int
        """
        self.socketConn.settimeout(secs_num)

    def __info(self, *args):
        if self.__print_info:
            print(*args)

    def __class__(self):
        return "server"
