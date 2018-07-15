"""
Get GPS records out of BlackVue video. Currently outputs CSV files,
with support for more formats added later.

Usage:
  blackvue_gps --to-csv <filename>

"""
import csv
import logging
import os
import re
import warnings
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
    previous_unix_ms = None
    with open(filename, 'r') as r:
        for line in r.readlines():
            if line.startswith('['):
                unix_ms = re.findall(r'(?!\[)[0-9]*(?=\])', line)[0]
                try:
                    parsed_nmea = pynmea2.parse(line.split(']')[-1])
                    if hasattr(parsed_nmea, 'latitude'):
                        if unix_ms != previous_unix_ms:
                            lat = parsed_nmea.latitude
                            lon = parsed_nmea.longitude
                            records.append(GPSPoint(unix_ms=unix_ms,
                                                    lat=lat,
                                                    lon=lon))
                            previous_unix_ms = unix_ms
                except ParseError:
                    warnings.warn('pynmea2 could not parse a line')
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
            logging.info(
                'Parsing the file {filename}'.format(filename=filename)
            )
            records = parse_blackvue_nmea(filename=filename)
            if tocsv:
                outputfilename = filename.replace('.mp4', '.gps.csv')
                list_of_namedtuple_to_csv(records, outputfilename)
        elif os.path.isdir(filename):
            logging.info(
                'Parsing all mp4-files in the folder {filename}'.format(
                    filename=filename
                )
            )
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
        else:
            logging.error('The file or folder {filename} does not '
                          'exist'.format(filename=filename)
                          )


if __name__ == "__main__":
    main(**docopt(__doc__))
