import mysql.connector
from config import Config


def get_connection():
    return mysql.connector.connect(**Config.db_params())


class DBContext:
    def __init__(self, dictionary: bool = False):
        self._dictionary = dictionary
        self.conn = None
        self.cur  = None

    def __enter__(self):
        self.conn = get_connection()
        self.cur  = self.conn.cursor(dictionary=self._dictionary)
        return self.conn, self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        return False  # no suprimir excepciones