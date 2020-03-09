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


def get_sensor_data(output_mode):
    """
    Uses the bme680 sensor to find and output the data that the sensor supports. This includes temperature (C),
    air pressure (hPa), humidity (%RH), gas resistance (Ohms) and air quality (%).

    :param output_mode: The format of the output data, if "readable" then the output is in a human readable format,
    if not then the output is in csv format.
    :return: A string containing the current temperature, air pressure, humidity, gas resistance and air quality.
    """
    output = ""

    if sensor.get_sensor_data():
        # We configure the output based on the command line argument.
        if output_mode == "readable":
            # Readable format.
            output += f"{sensor.data.temperature:.2f} C, {sensor.data.pressure:.2f} hPa, {sensor.data.humidity:.2f} %RH"
        else:
            # csv format.
            output += f"{sensor.data.temperature:.2f},{sensor.data.pressure:.2f},{sensor.data.humidity:.2f}"

        # Since the gas resistance data is dependant on the hot plate we ensure that it is stable before reading.
        if sensor.data.heat_stable:
            if output_mode == "readable":
                # Readable format.
                output += f", {sensor.data.gas_resistance} Ohms\n"
            else:
                # csv format.
                output += f",{sensor.data.gas_resistance}\n"
        else:
            output += "\n"

    return output


# TODO: Add air quality to both outputs. Could be done by adding an "get_air_quality" function.
def get_air_quality(gas_resistance, humidity):
    pass

# TODO: Handle csv header elsewhere.
# TODO: Put the data in a file.
