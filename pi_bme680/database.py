"""
Database file for inserting and querying from the database related to the bme680 sensor. This file contains supportive
database related functions that provide the necessary functionality needed for the AQT assistant. This includes
functions for querying that support the temperature and air quality warnings together with data visualization and
insertion of data.
"""
import psycopg2


def get_database_connection():
    """
    Function that makes database connections easier to work with since there is multiple functions that
    each need a connection.
    :return: A database connection to the AQT assistant database that is running on the Raspberry pi zero.
    """
    try:
        return psycopg2.connect(user="pi",
                                # TODO: Put this password in a config file that is not on github.
                                password="***REMOVED***",
                                host="***REMOVED***",
                                port="***REMOVED***",
                                database="aqtassistant")

    except (Exception, psycopg2.Error) as pg_error:
        print("Error while working with PostgreSQL" + pg_error)


def insert_sensor_data(data, connection, cursor):
    """
    Inserts a single data measurement into the LivingRoom table. We only insert temperate, air pressure, humidity,
    gas resistance and air quality since time is handled by the default value (now()) and the id is auto incrementing.
    :return:
    """
    # Creating the INSERT query that insert the data into the LivingRoom table.
    pg_insert_query = "insert into livingroom values (%s, %s, %s, %s, %s)"

    # Executing the query while also replacing the placeholders in the query with the actual data.
    cursor.execute(pg_insert_query, data)

    # Committing the changes to the database, hereby ending the transaction.
    connection.commit()
