"""
Database file for creating tables and inserting and querying from the database related to the bme680 sensor. This file
contains supportive functions that provide the necessary functionality needed for the AQT assistant. This includes
functions for creating a table that can hold the data and querying functions that support the temperature and air
quality warnings together with data visualization.
"""
import psycopg2

try:
    connection = psycopg2.connect(user="pi",
                                  password="***REMOVED***",
                                  host="***REMOVED***",
                                  port="***REMOVED***",
                                  database="aqtassistant")
    cursor = connection.cursor()
    pg_select_query = "select * from livingroom"

    cursor.execute(pg_select_query)
    print(cursor.fetchall())

except (Exception, psycopg2.Error) as error:
    print("Error while working with PostgreSQL" + error)
finally:
    # Closing database connection
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
