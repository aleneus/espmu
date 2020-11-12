"""Commonly used functions for parsing PMU Frames."""

import codecs
import struct


def hexToBin(hex_str, num_of_bits):
    """Converts hex string to binary

    :param hex_str: Hex value in string format
    :type hex_str: str
    :param num_of_bits: Number of bits to convert
    :type num_of_bits: int

    :return: bits representing the hex values
    """
    return bin(int(hex_str, 16))[2:].zfill(num_of_bits)


def bytesToHexStr(bytes_input):
    """Converts byte array to hex str

    :param bytes_input: byte array to convert
    :type bytes_input: byte-array

    :return: Hex string representing bytes_input
    """

    return codecs.encode(bytes_input, 'hex').decode('ascii')


def doubleToHex(f):
    """Converts double to hex

    :param f: Double value to convert
    :type f: double

    :return: Hex representation of double value
    """
    return hex(struct.unpack('!Q', struct.pack('!d', f))[0])


def doubleToHexStr(f):
    """Converts double to hex str

    :param f: Double value to convert
    :type f: double

    :return: Hex string representation of double value
    """
    return hex(struct.unpack('!Q', struct.pack('!d', f))[0])[2:]


def doubleToBytes(f):
    """Converts double to byte array

    :param f: Double value to convert
    :type f: double

    :return: Byte array representation of double value
    """
    return struct.pack('d', f)


def bytesToFloat(b):
    """Converts byte array to double

    :param b: Byte array to convert
    :type b: byte-array

    :return: Float value
    """
    return struct.unpack('d', b)[0]


def intToBytes(i):
    """Converts unsigned int to byte array

    :param i: Integer value to convert
    :type i: int

    :return: Byte array representing i
    """
    return struct.pack('!I', i)


def intToHexStr(i):
    """Converts int to hex

    :param i: Integer value to convert
    :type i: int

    :return: Hex string representing i
    """
    return hex(i)[2:]
