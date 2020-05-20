"""
Database file for inserting and querying from the database related to the bme680 sensor. This file contains supportive
database related functions that provide the necessary functionality needed for the AQT assistant. This includes
functions for querying that support the temperature and air quality warnings together with data visualization and
insertion of data.
"""
import psycopg2
import json


class Database:
    """
    Database that can be used to query from and insert data into the livingroom database table.
    """
    def __init__(self):
        # Creating a connection to the PostgreSQL database.
        self.connection = self.get_database_connection()

        # Creating a cursor object that can be used for INSERT statements.
        self.cursor = self.connection.cursor()

    @staticmethod
    def get_database_connection():
        """
        Function that makes database connections easier to work with since there is multiple functions that
        each need a connection.
        :return: A database connection to the AQT assistant database that is running on the Raspberry pi zero.
        """

        # Pulling the database settings from the config file.
        with open("resources/database_config.json", "r") as config:
            config_dict = json.load(config)

            try:
                return psycopg2.connect(user=config_dict["user"],
                                        # TODO: Change password.
                                        password=config_dict["password"],
                                        host=config_dict["host"],
                                        port=config_dict["port"],
                                        database=config_dict["database"])

            except (Exception, psycopg2.Error) as pg_error:
                print("Error while working with PostgreSQL" + str(pg_error))

    def insert_sensor_data(self, data):
        """
        Inserts a single data measurement into the LivingRoom table. We only insert temperate, air pressure,
        humidity, gas resistance and air quality since time is handled by the default value (now()) and the id is
        auto incrementing.
        :return:
        """
        # Creating the INSERT query that insert the data into the LivingRoom table.
        pg_insert_query = "insert into livingroom values (%s, %s, %s, %s, %s)"

        # Executing the query while also replacing the placeholders in the query with the actual data.
        self.cursor.execute(pg_insert_query, data)

        # Committing the changes to the database, hereby ending the transaction.
        self.connection.commit()

    def get_sensor_data(self, column_names, limit):
        """
        Retrieves the latest sensor data from the livingroom table according to the settings given in the parameters.

        :param column_names: The columns that we wish to retrieve.
        :param limit: The amount of rows that we wish to retrieve.
        :return:
        """
        pg_select_query = "SELECT " + column_names + " FROM livingroom ORDER BY id DESC LIMIT " + str(limit)

        self.cursor.execute(pg_select_query)

        return self.cursor.fetchall()

    def close(self):
        """Closes the connection and the cursor."""
        self.connection.close()
        self.cursor.close()
