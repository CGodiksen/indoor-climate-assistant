"""
This file should be run from the Raspberry pi zero that is connected to the bme680 sensor. Running this file starts an
infinite loop that inserts data into the PostgreSQL database.
"""
from database import database
import sensor
import time


if __name__ == '__main__':
    # Creating a connection to the PostgreSQL database.
    connection = database.get_database_connection()

    # Creating a cursor object that can be used for INSERT statements.
    cursor = connection.cursor()

    gas_baseline = sensor.burn_in_sensor()
    # Wrapping the infinite loop in a try-except to support command line keyboard interruption.
    try:
        while True:
            # Getting the current data from the bme680 sensor.
            data = sensor.get_sensor_data(gas_baseline)

            # Inserting the data into the database.
            database.insert_sensor_data(data, connection, cursor)

            time.sleep(1)
    except KeyboardInterrupt:
        cursor.close()
        connection.close()
