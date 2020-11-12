"""Example of reading data from PMU."""
import os
import sys
from time import sleep, gmtime, strftime

sys.path.insert(0, os.path.abspath('.'))
from espmu.streaming import PmuStreamDataReader


class ARGS:
    """CLI arguments."""
    ip = None
    tcp_port = None
    idcode = None
    name = None


def parse_args():
    """Parse CLI arguments."""

    if len(sys.argv) < 5:
        print("syntax: read_conf.py ip port idcode name")
        sys.exit(1)

    ARGS.ip = sys.argv[1]
    ARGS.tcp_port = int(sys.argv[2])
    ARGS.idcode = int(sys.argv[3])
    ARGS.name = sys.argv[4]


def main():
    """Run example."""

    parse_args()

    reader = PmuStreamDataReader()

    if not reader.connect(ARGS.ip, ARGS.tcp_port, ARGS.idcode):
        print("The source is unreachable")
        sys.exit(1)

    if not reader.is_time_reliable():
        print("Time is not reliable, but I'll try to get data. Wait...")
        sleep(3)

    stations = reader.stations()
    if not stations:
        sys.exit(1)

    ind, found = _search_index(ARGS.name, reader, 0)
    if not found:
        sys.exit(1)

    reader.start()

    def __stop():
        print("wait...")
        reader.stop()
        sleep(1)

    try:
        while True:
            try:
                samples = reader.get_full_samples(station_ind=0)
            except Exception as ex:
                print(ex)
                __stop()
            else:
                t, f, x = _extract_data(samples, ind)
                print("{} {} {}".format(_repr_time(t), round(f, 2), x))

    except KeyboardInterrupt:
        print()
        __stop()

    reader.disconnect()


def _repr_time(t: int):
    return strftime("%Y-%m-%d %H:%M:%S:{}".
                    format(round(1000 * (t % 1))), gmtime(t))


def _extract_data(samples, ind: int):
    t = samples[0][0]
    f = samples[0][1]
    x = samples[0][ind]
    return t, f, x


def _search_index(name, reader, station_ind) -> (int, bool):
    ind = 2

    for ph in reader.phasors(station_ind):
        ind = ind + 1
        if ph == name:
            return ind, True

    for an in reader.analogs(station_ind):
        ind = ind + 1
        if an == name:
            return ind, True

    return ind, False


if __name__ == "__main__":
    main()
