import mysql.connector
from db_data import work_shifts


def get_difference(date1, date2):
    if date2 > date1:
        delta = date2 - date1
        return delta.seconds // 3600
    delta = date1 - date2
    return delta.seconds // 3600


def open_db():
    return mysql.connector.connect(
        host=work_shifts.get('host'),
        user=work_shifts.get('user'),
        password=work_shifts.get('password'),
        database=work_shifts.get('database')
    )
