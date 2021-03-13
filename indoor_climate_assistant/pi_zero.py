"""
This file should be run from the Raspberry pi zero that is connected to the bme680 sensor. Running this file starts an
infinite loop that inserts data into the PostgreSQL database.
"""
from indoor_climate_assistant.database import Database
import time
from indoor_climate_assistant import sensor

if __name__ == '__main__':
    # Creating a connection to the PostgreSQL database.
    aqtassistant_db = Database()

    gas_baseline = sensor.burn_in_sensor()

    counter = 0
    # Wrapping the infinite loop in a try-except to support command line keyboard interruption.
    try:
        while True:
            counter += 1

            # Getting the current data from the bme680 sensor.
            data = sensor.get_sensor_data(gas_baseline)

            # Every 60 seconds we insert the data into the database.
            if counter % 60 == 0:
                aqtassistant_db.insert_sensor_data(data)

            time.sleep(1)
    except KeyboardInterrupt:
        # Closing the database connection if execution is halted.
        aqtassistant_db.close()
