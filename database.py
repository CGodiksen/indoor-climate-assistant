"""
Database file for inserting and querying from the database related to the bme680 sensor. This file
contains supportive functions that provide the necessary functionality needed for the AQT assistant. This includes
functions for querying that support the temperature and air quality warnings together with data visualization and
continuous insertion of data.
"""
import psycopg2
import sensor
import time


def get_database_connection():
    try:
        return psycopg2.connect(user="pi",
                                password="***REMOVED***",
                                host="***REMOVED***",
                                port="***REMOVED***",
                                database="aqtassistant")

    except (Exception, psycopg2.Error) as pg_error:
        print("Error while working with PostgreSQL" + pg_error)


def insert_sensor_data():
    # Creating a connection to the PostgreSQL database.
    connection = get_database_connection()

    # Creating a cursor object that can be used for INSERT statements.
    cursor = connection.cursor()

    gas_baseline = sensor.burn_in_sensor()
    # Wrapping the infinite loop in a try-except to support command line keyboard interruption.
    try:
        while True:
            # Getting the current data from the bme680 sensor.
            data = sensor.get_sensor_data(gas_baseline)

            # Creating the INSERT query that insert the data into the LivingRoom table.
            pg_insert_query = "insert into livingroom values (%s, %s, %s, %s, %s)"

            # Executing the query while also replacing the placeholders in the query with the actual data.
            cursor.execute(pg_insert_query, data)

            # Committing the changes to the database, hereby ending the transaction.
            connection.commit()

            time.sleep(1)
    except KeyboardInterrupt:
        cursor.close()
        connection.close()
