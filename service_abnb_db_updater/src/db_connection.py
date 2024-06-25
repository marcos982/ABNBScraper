# db_connection.py
from datetime import datetime
from decimal import Decimal
import json
import numpy as np
import psycopg2
from psycopg2 import pool
from psycopg2.extras import Json

class ABNBDBScraperConnection:
    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ABNBDBScraperConnection, cls).__new__(cls)
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10,
                host="db",
                port=5432,
                database="ABNSCraper",
                user="postgres",
                password="password"
            )
        return cls._instance

    def get_connection(self):
        return self._connection_pool.getconn()

    def put_connection_back(self, conn):
        self._connection_pool.putconn(conn)

    def close_all_connections(self):
        self._connection_pool.closeall()

    def execute_query(self, query, params=None):
        """
            Execute a SQL query and return the result.

            For SELECT queries, returns a tuple of (rows, column_names).
            For other queries, commits the transaction and returns (None, None).

            :param query: SQL query string.
            :param params: Optional parameters for the SQL query.
            :return: A tuple containing the query results and column names, or (None, None).
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                if query.lower().startswith("select"):
                    rows = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    result = {'column_names': column_names, 'rows': rows}
                else:
                    conn.commit()
                    result = None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_connection_back(conn)
        return result
    
    def insert_record(self, record):
        """
        Insert data into the database.

        :param data: A dictionary containing the data to be inserted.
        """
        conn = None
        try:
            # TODO: raise exception for id, checkin or checkouyt invalid
            name = record.get("name") if record.get("name") is not None else None            
            id = record.get("id") if record.get("id") is not None else None
            location = json.dumps(record.get("location")) if record.get("location") is not None else None
            price = record.get("price") if record.get("price") is not None else None
            pricecleaning = record.get("pricecleaning") if record.get("pricecleaning") is not None else None
            checkin = record.get("checkin") if record.get("checkin") is not None else None
            checkout = record.get("checkout") if record.get("checkout") is not None else None

            # Connect to your database
            conn = self.get_connection()
            cursor = conn.cursor()
            # Construct the SQL statement
            sql = "INSERT INTO abnscraper (id, name, location, price, pricecleaning, checkin, checkout, rented, created_ts, updating_logs) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (id, name, location, price, pricecleaning, checkin, checkout, False, datetime.now(), None)
            # Execute the SQL statement
            cursor.execute(sql, params)
            # Commit the changes
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            if conn is not None:
                conn.rollback()
                
        finally:
            if conn is not None:
                cursor.close()
                self.put_connection_back(conn)

    def update_database(self, pkey, updating_log):
        """
        Update database records based on the updating_log JSON object.

        :param updating_log: A dictionary containing the record id, updated_at timestamp,
                            and a list of updated_fields with field names and their old and new values.
        """

        def custom_encoder(obj):
            if isinstance(obj, (Decimal, np.number)):
                return float(obj)  # O str(obj) se preferisci rappresentarlo come stringa
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        conn = None
        try:
            # Connect to your database
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT updating_logs FROM abnscraper WHERE pkey = %s", (pkey,))
            result = cursor.fetchone()
            current_logs = result[0] if result and result[0] is not None else []
            current_logs.append(updating_log)
            cursor.execute("UPDATE abnscraper SET updating_logs = %s WHERE pkey = %s", (json.dumps(current_logs, default=custom_encoder), pkey))

            # Iterate over each updated field and construct and execute the UPDATE statement
            for update in updating_log['updated_fields']:
                field_name = update['field_updated']
                new_value = update['new_value']

                # Construct the SQL statement
                sql = f"UPDATE abnscraper SET {field_name} = %s WHERE pkey = %s"
                # Execute the SQL statement
                cursor.execute(sql, (Json(new_value), pkey))

            # Commit the changes
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            if conn is not None:
                conn.rollback()
                
        finally:
            if conn is not None:
                cursor.close()
                self.put_connection_back(conn)