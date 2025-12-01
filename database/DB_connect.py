import sqlite3


class DBConnect:
    DB_PATH = "database/xnatpic.db"

    @staticmethod
    def get_connection():
        try:
            connection = sqlite3.connect(DBConnect.DB_PATH)
            connection.row_factory = sqlite3.Row
            return connection
        except sqlite3.Error as exc:
            print(
                f"Unable to connect to the credentials database: {exc}"
            )
            return None
