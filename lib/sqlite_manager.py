import sqlite3 as sql

from os.path import exists
from datetime import datetime as dt
from lib.webscraping.get_btp_data_async import asyncrun_get_btp_data as gbd


DB_PATH = "./app.sqlite"

BTPS_TABLE_NAME = "BTPs"
APP_DATA_TABLE_NAME = "AppData"


def update_btp_last_update(cursor):
    """
    Update the "btp_data_last_update" row in the AppData table with the current timestamp.

    :param cursor: A SQLite3 cursor object.
    """

    cursor.execute('UPDATE AppData SET value = CURRENT_TIMESTAMP WHERE name = "btp_data_last_update"')


def first_insert_btp_db(cursor):
    """
    Check if BTP table is empty and fill it with data fetched from the web.

    :param cursor: A SQLite3 cursor object.
    :return: True if the table was populated, False otherwise.
    """

    if cursor.execute(f'SELECT COUNT(*) FROM {BTPS_TABLE_NAME}').fetchone()[0] == 0:
        btps = gbd()

        for btp in btps:
            maturity_date = dt.strptime(btp.maturity_date, "%d/%m/%y").strftime("%Y-%m-%d")

            cursor.execute(f'INSERT INTO {BTPS_TABLE_NAME} (ISIN, name, market_price, variation, coupon_periodity, coupon, maturity_date, nominal_value, gross_yield, net_yield) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (btp.isin, btp.description, btp.market_price, btp.variation, btp.coupon_periodity, btp.coupon, maturity_date, btp.nominal_value, btp.gross_yield, btp.net_yield))

        return True

    return False


def initialize_db():
    """
    Initialize database if it does not exist.

    This function creates the database file at `DB_PATH` if it does not exist.
    It then creates a table named `BTPS_TABLE_NAME` with the following columns:
    - `ISIN`: TINYTEXT PRIMARY KEY
    - `name`: TINYTEXT
    - `market_price`: FLOAT
    - `variation`: FLOAT
    - `coupon_periodity`: TINYTEXT
    - `coupon`: FLOAT
    - `maturity_date`: DATE
    - `nominal_value`: INTEGER
    - `gross_yield`: FLOAT
    - `net_yield`: FLOAT

    Returns True if the database was successfully initialized, False otherwise.
    """

    connection = sql.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(f'CREATE TABLE IF NOT EXISTS {BTPS_TABLE_NAME} (ISIN TINYTEXT PRIMARY KEY, name TINYTEXT, market_price FLOAT, variation FLOAT, coupon_periodity TINYTEXT, coupon FLOAT, maturity_date DATE, nominal_value INTEGER, gross_yield FLOAT, net_yield FLOAT)')
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {APP_DATA_TABLE_NAME} (name TINYTEXT PRIMARY KEY,value TINYTEXT)')
    cursor.execute(f'INSERT INTO {APP_DATA_TABLE_NAME} (name, value) VALUES (?, ?)', ('btp_data_last_update', None))

    first_insert_btp_db(cursor)
    update_btp_last_update(cursor)

    connection.commit()
    connection.close()

    if not exists(DB_PATH):
        return False

    return True


if __name__ == "__main__":
    initialize_db()
