"""
Get GPS records out of BlackVue video. Currently outputs CSV files,
with support for more formats added later.

Usage:
  blackvue_gps --to-csv <filename>

"""
import csv
import os
import re
from collections import namedtuple

import pynmea2
from docopt import docopt
from pynmea2 import ParseError

import blackclue

GPSPoint = namedtuple('GPSPoint', ['unix_ms', 'lat', 'lon'])


def parse_blackvue_nmea(filename):
    """
    Parse a NMEA file as created by BlackVue, meaning there is a unix timestamp
    in milliseconds before the NMEA string.

    :param filename: the location of the BlackVue NMEA as string
    :return: a list of GPSPoint
    """
    filename = filename.replace(".mp4", ".nmea")
    records = []
    with open(filename, 'r') as r:
        for line in r.readlines():
            if line.startswith('['):
                # TODO make proper regex and less string slicing
                unix_ms = re.findall(r'(?=\[).*(?=\])', line)[0][1:]
                try:
                    parsed_nmea = pynmea2.parse(line[len(unix_ms) + 2:])
                    if hasattr(parsed_nmea, 'latitude'):
                        lat, lon = parsed_nmea.latitude, parsed_nmea.longitude
                        records.append(GPSPoint(unix_ms=unix_ms,
                                                lat=lat,
                                                lon=lon))
                except ParseError:
                    print('ParseError', line[len(unix_ms) + 2:])
    return records


def list_of_namedtuple_to_csv(list_of_tuples, outputfilename):
    """
    Write a list of namedtuples to a csv file.

    :param list_of_tuples: a list of namedtuples of the same type
    :param outputfilename: a target output filename
    """
    fields = []
    if len(list_of_tuples) > 0:
        fields = list_of_tuples[0]._fields
    with open(outputfilename, 'w') as w:
        csvwriter = csv.writer(w)
        csvwriter.writerow(fields)
        for row in list_of_tuples:
            csvwriter.writerow(row)


def main(**kwargs):
    if len(kwargs) == 0:
        kwargs = docopt(__doc__)
    tocsv = kwargs.get('--to-csv')
    filename = kwargs.get('<filename>')
    if filename:
        if os.path.isfile(filename):
            records = parse_blackvue_nmea(filename=filename)
            if tocsv:
                outputfilename = filename.replace('.mp4', '.gps.csv')
                list_of_namedtuple_to_csv(records, outputfilename)
        elif os.path.isdir(filename):
            foldername = filename
            for filename in filter(lambda x: x.endswith('.mp4'),
                                   os.listdir(foldername)):
                blackclue.dump(file=[os.path.join(foldername, filename)],
                               dump_embedded=True,
                               dump_raw_blocks=False,
                               extended_scan=False,
                               verbose=False)
                records = parse_blackvue_nmea(filename=os.path.join(
                    foldername, filename))
                if tocsv:
                    outputfilename = filename.replace('.mp4', '.gps.csv')
                    list_of_namedtuple_to_csv(records, os.path.join(
                        foldername, outputfilename))


if __name__ == "__main__":
    main(**docopt(__doc__))
