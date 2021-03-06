import csv
from datetime import datetime
import math
import re
import os
from os.path import exists

def converter_nmea_to_csv(INPUT_FILENAME, OUTPUT_FILENAME) :
    # open the input file in read mode
    with open(INPUT_FILENAME, 'r') as input_file:

        # open the output file in write mode
        with open(OUTPUT_FILENAME, 'wt') as output_file:

            # create a csv reader object from the input file (nmea files are basically csv)
            reader = csv.reader(input_file)

            # create a csv writer object for the output file
            writer = csv.writer(output_file, delimiter=',', lineterminator='\n')

            # write the header line to the csv file
            writer.writerow(['date_and_time', 'lat', 'lon', 'speed'])

            # iterate over all the rows in the nmea file
            for row in reader:

                # skip all lines that do not start with $GPRMC
                if not row[0].startswith('$GPRMC'):
                    continue

                else:

                    # for each row, fetch the values from the row's columns
                    # columns that are not used contain technical GPS stuff that you are probably not interested in
                    time = row[1]
                    warning = row[2]
                    lat = row[3]
                    lat_direction = row[4]
                    lon = row[5]
                    lon_direction = row[6]
                    speed = row[7]
                    date =  row[9]

                    # if the "warning" value is "V" (void), you may want to skip it since this is an indicator for an incomplete data row)
                    if warning == 'V':
                        continue

                    # merge the time and date columns into one Python datetime object (usually more convenient than having both separately)
                    date_and_time = datetime.strptime(date + ' ' + time, '%d%m%y %H%M%S.%f')

                    # convert the Python datetime into your preferred string format, see http://www.tutorialspoint.com/python/time_strftime.htm for futher possibilities
                    date_and_time = date_and_time.strftime('%y-%m-%d %H:%M:%S.%f')[:-3] # [:-3] cuts off the last three characters (trailing zeros from the fractional seconds)

                    # lat and lon values in the $GPRMC nmea sentences come in an rather uncommon format. for convenience, convert them into the commonly used decimal degree format which most applications can read.
                    # the "high level" formula for conversion is: DDMM.MMMMM => DD + (YY.ZZZZ / 60), multiplicated with (-1) if direction is either South or West
                    # the following reflects this formula in mathematical terms.
                    # lat and lon have to be converted from string to float in order to do calculations with them.
                    # you probably want the values rounded to 6 digits after the point for better readability.
                    lat = round(math.floor(float(lat) / 100) + (float(lat) % 100) / 60, 6)
                    if lat_direction == 'S':
                        lat = lat * -1

                    lon = round(math.floor(float(lon) / 100) + (float(lon) % 100) / 60, 6)
                    if lon_direction == 'W':
                        lon = lon * -1

                    # speed is given in knots, you'll probably rather want it in km/h and rounded to full integer values.
                    # speed has to be converted from string to float first in order to do calculations with it.
                    # conversion to int is to get rid of the tailing ".0".
                    speed = int(round(float(speed) * 1.852, 0))

                    # write the calculated/formatted values of the row that we just read into the csv file
                    writer.writerow([date_and_time, lat, lon, speed])

def automation_converter():
    FOLDER_INPUT_NAME = './data'
    FOLDER_OUTPUT_NAME = './output'

    # check if data's and output's folder are already exists
    if not(os.path.exists(FOLDER_INPUT_NAME)):
        os.mkdir('data')

    if not(os.path.exists(FOLDER_OUTPUT_NAME)):
        os.mkdir('output')

    FILE_IN_DATA_FOLDER = os.listdir(FOLDER_INPUT_NAME)
    FILE_IN_OUTPUT_FOLDER = os.listdir(FOLDER_OUTPUT_NAME)
      
    # find exactly the filename with regex
    SEARCH_FILENAME = re.compile(r'[a-zA-Z]+([0-9]+(_[0-9]+)+)')

    if(len(FILE_IN_DATA_FOLDER) != 0 and len(FILE_IN_OUTPUT_FOLDER) != 0):
        for data in FILE_IN_DATA_FOLDER:
            for output in FILE_IN_OUTPUT_FOLDER:
                print(data)
                print(output)
                data_name = SEARCH_FILENAME.search(data)
                output_name = SEARCH_FILENAME.search(output)
                print(data_name)
                print(output_name)

                if(output_name == data_name):
                    continue
                else:
                    INPUT_FILENAME = FOLDER_INPUT_NAME + '/' + data
                    OUTPUT_FILENAME = FOLDER_OUTPUT_NAME + '/' + SEARCH_FILENAME.search(data).group() +'.csv'
                    converter_nmea_to_csv(INPUT_FILENAME, OUTPUT_FILENAME)
    elif(len(FILE_IN_DATA_FOLDER) == 0 and len(FILE_IN_OUTPUT_FOLDER) == 0):
        return False
    else:
       for data in FILE_IN_DATA_FOLDER:
            INPUT_FILENAME = FOLDER_INPUT_NAME + '/' + data
            OUTPUT_FILENAME = FOLDER_OUTPUT_NAME + '/' + SEARCH_FILENAME.search(data).group() +'.csv'
            converter_nmea_to_csv(INPUT_FILENAME, OUTPUT_FILENAME)

automation_converter()

