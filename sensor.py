"""
This file contains the code for extracting data from the bme680 sensor. The file should be run from the
raspberry pi that is connected to the sensor.

The file can be run in two different modes:
readable: Outputting the data with supportive notation that helps in understanding the output.
csv (standard): Outputting only the pure data as to minimize the size of the output.

The file outputs temperature (C), air pressure (hPa), humidity (%RH), gas resistance (Ohms) and air quality (%).
"""
import bme680
import time
import sys

# Creating the sensor object that represents the bme680 sensor.
sensor = bme680.BME680()

# Oversample settings set the trade-off between accuracy and noise. Higher oversampling = less noise, less accuracy.
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)

# The filter setting protects against momentary changes in the environment, like a door slamming.
sensor.set_filter(bme680.FILTER_SIZE_3)

# Settings regarding the gas resistance reading.
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# First print the csv header if we are not printing human readable data.
if sys.argv[0] != "readable":
    print("temperature,air_pressure,humidity,gas_resistance,air_quality")

# Printing the readable data in an infinite loop.
while True:
    if sensor.get_sensor_data():
        # We configure the output based on the command line argument.
        if sys.argv[0] == "readable":
            # Readable format.
            output = "{0:.2f} C, {1:.2f} hPa, {2:.2f} %RH".format(sensor.data.temperature, sensor.data.pressure,
                                                                  sensor.data.humidity)
        else:
            # csv format.
            output = "{0:.2f},{1:.2f},{2:.2f}".format(sensor.data.temperature, sensor.data.pressure,
                                                      sensor.data.humidity)

        # Since the gas resistance data is dependant on the hot plate we ensure that it is stable before reading.
        if sensor.data.heat_stable:
            if sys.argv[0] == "readable":
                # Readable format.
                print("{0}, {1} Ohms".format(output, sensor.data.gas_resistance))
            else:
                # csv format.
                print("{0},{1}".format(output, sensor.data.gas_resistance))
        else:
            print(output)

    time.sleep(1)

# TODO: Add air quality to both outputs. Could be done by adding an "get_air_quality" function.
