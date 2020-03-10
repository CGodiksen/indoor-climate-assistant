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

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

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


def get_sensor_data(output_mode, gas_baseline):
    """
    Uses the bme680 sensor to find and output the data that the sensor supports. This includes temperature (C),
    air pressure (hPa), humidity (%RH), gas resistance (Ohms) and air quality (%).

    :param output_mode: The format of the output data, if "readable" then the output is in a human readable format,
    if not then the output is in csv format.
    :param gas_baseline: The gas baseline obtained from the burn in period.
    :return: A string containing all data in the requested format.
    """
    output = ""

    if sensor.get_sensor_data():
        temperature = sensor.data.temperature
        pressure = sensor.data.pressure
        humidity = sensor.data.humidity

        # We configure the output based on the command line argument.
        if output_mode == "readable":
            # Readable format.
            output += "{0:.2f} C, {1:.2f} hPa, {2:.2f} %RH".format(temperature, pressure, humidity)
        else:
            # csv format.
            output += "{0:.2f},{1:.2f},{2:.2f}".format(temperature, pressure, humidity)

        # Since the gas resistance data is dependant on the hot plate we ensure that it is stable before reading.
        if sensor.data.heat_stable:
            gas_resistance = sensor.data.gas_resistance
            if output_mode == "readable":
                # Readable format.
                output += ", {0} Ohms, {1:.2f}%".format(gas_resistance,
                                                        get_air_quality(gas_resistance, humidity, gas_baseline))
            else:
                # csv format.
                output += ",{0},{1:.2f}".format(gas_resistance, get_air_quality(gas_resistance, humidity, gas_baseline))

    return output


def get_air_quality(gas_resistance, humidity, gas_baseline):
    """
    Runs the sensor for a burn-in period, then uses a combination of relative humidity and gas resistance
    to estimate indoor air quality as a percentage.

    :param gas_resistance: Current gas resistance from the bme680 sensor.
    :param humidity: Current humidity from the bme680 sensor.
    :param gas_baseline: The gas baseline obtained from the burn in period.
    :return: Air quality based on the gas resistance and humidity.
    """
    # Set the humidity baseline to 40%, an optimal indoor humidity.
    hum_baseline = 40.0

    # This sets the balance between humidity and gas reading in the calculation of air_quality_score
    # (25:75, humidity:gas)
    hum_weighting = 0.25

    gas = gas_resistance
    gas_offset = gas_baseline - gas

    hum = humidity
    hum_offset = hum - hum_baseline

    # Calculate hum_score as the distance from the hum_baseline.
    if hum_offset > 0:
        hum_score = (100 - hum_baseline - hum_offset)
        hum_score /= (100 - hum_baseline)
        hum_score *= (hum_weighting * 100)

    else:
        hum_score = (hum_baseline + hum_offset)
        hum_score /= hum_baseline
        hum_score *= (hum_weighting * 100)

    # Calculate gas_score as the distance from the gas_baseline.
    if gas_offset > 0:
        gas_score = (gas / gas_baseline)
        gas_score *= (100 - (hum_weighting * 100))

    else:
        gas_score = 100 - (hum_weighting * 100)

    # Calculate air_quality_score.
    air_quality_score = hum_score + gas_score

    return air_quality_score


def burn_in_sensor(burn_in_time=300):
    """
    Warms up the sensor for the specified amount of time to optimize the gas resistance data readings.

    :param burn_in_time: The amount of time in seconds that the sensor should use to warm up.
    The recommend time is 5 minutes for optimal results.
    :return: A gas baseline that can be used for calculating air quality.
    """
    # Start time and current time are used to to handle the burn in time of 5 minutes.
    start_time = time.time()
    curr_time = time.time()

    burn_in_data = []

    # Collect gas resistance burn-in values, then use the average of the last 50 values to set the upper limit
    # for calculating gas_baseline.
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            time.sleep(1)

    return sum(burn_in_data[-50:]) / 50.0


if __name__ == '__main__':
    gas_baseline = burn_in_sensor()
    try:
        while True:
            print(get_sensor_data("readable", gas_baseline))

            time.sleep(1)
    except KeyboardInterrupt:
        pass
# TODO: Handle csv header elsewhere.
# TODO: Put the data in a file.
