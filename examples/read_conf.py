import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from espmu.streaming import PmuStreamDataReader


class ARGS:
    ip = None
    tcp_port = None
    idcode = None


def parse_args():
    if len(sys.argv) < 4:
        print("syntax: read_conf.py ip port idcode")
        sys.exit(1)

    ARGS.ip = sys.argv[1]
    ARGS.tcp_port = int(sys.argv[2])
    ARGS.idcode = int(sys.argv[3])


def main():
    parse_args()

    reader = PmuStreamDataReader()

    if not reader.connect(ARGS.ip, ARGS.tcp_port, ARGS.idcode):
        print("The source is unreachable")
        sys.exit(1)

    print_header(1, "Connection details")

    print("* IP: {}".format(ARGS.ip))
    print("* PORT: {}".format(ARGS.tcp_port))
    print("* IDCODE: {}".format(ARGS.idcode))
    print("")

    print_header(1, "Time and frequency")

    if reader.is_time_reliable():
        print("Time is reliable\n")
    else:
        print("Time is not reliable\n")

    print("fs = {} Hz\n".format(reader.rate()))

    stations = reader.stations()

    for ind, name in enumerate(stations):
        print_header(1, name)

        print_header(2, "Phasors")
        for ph in reader.phasors(ind):
            print("{}".format(ph))
        print("")

        print_header(2, "Analogs")
        for an in reader.analogs(ind):
            print("{}".format(an))

    reader.disconnect()


def print_header(level, title):
    for i in range(level):
        print("#", end="")
    print(" ", end="")
    print(title)
    print("")


if __name__ == "__main__":
    main()
