"""
This file should be run from the Raspberry pi zero that is connected to the bme680 sensor. Running this file starts an
infinite loop that inserts data into the PostgreSQL database.
"""
from database import Database
import time
import sensor


if __name__ == '__main__':
    # Creating a connection to the PostgreSQL database.
    aqtassistant_database = Database()

    gas_baseline = sensor.burn_in_sensor()
    # Wrapping the infinite loop in a try-except to support command line keyboard interruption.
    try:
        while True:
            # Getting the current data from the bme680 sensor.
            data = sensor.get_sensor_data(gas_baseline)

            # Inserting the data into the database.
            aqtassistant_database.insert_sensor_data(data)

            time.sleep(1)
    except KeyboardInterrupt:
        # Closing the database connection if execution is halted.
        aqtassistant_database.close()
