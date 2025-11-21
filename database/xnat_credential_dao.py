import sqlite3

from database.xnat_credential_dto import XnatCredentialDto


class XnatCredentialDao:
    @staticmethod
    def get_all_credentials():
        query = """SELECT c.*
                FROM xnat_credentials c"""

        cnx = sqlite3.connect('database/xnatpic.db')
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()

        cursor.execute(query)

        result = []
        for row in cursor:
            result.append(
                XnatCredentialDto(row["address"], row["username"],
                               row["password"], bool(row["remember"]))
            )

        cursor.close()
        cnx.close()

        return result

    @staticmethod
    def delete_credential():
        query_delete_rows = "DELETE FROM xnat_credentials"

        query_reset_ai = """DELETE FROM sqlite_sequence
                            WHERE name=?"""

        cnx = sqlite3.connect('database/xnatpic.db')
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()

        success = False

        try:
            cursor.execute(query_delete_rows)
            cursor.execute(
                query_reset_ai,
                ('xnat_credentials',)
            )
            cnx.commit()
            success = True
        except Exception as e:
            print("Error", str(e))
            cnx.rollback()

        cursor.close()
        cnx.close()

        return success

    @staticmethod
    def update_remember():
        query = """UPDATE nome_tabella
                   SET nome_colonna = ?"""

        cnx = sqlite3.connect('database/xnatpic.db')
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()

        success = False

        try:
            cursor.execute(query, (0,))
            cnx.commit()
            success = True
        except Exception as e:
            print("Error", str(e))
            cnx.rollback()

        cursor.close()
        cnx.close()

        return success

    @staticmethod
    def insert_new_credential(address, username, password, remember):
        query = """INSERT INTO xnat_credentials
                                (address, username, password, remember)
                                VALUES (?,?,?,?)"""

        cnx = sqlite3.connect('database/xnatpic.db')
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()

        success = False

        try:
            cursor.execute(
                query,
                (
                    address,
                    username,
                    password,
                    int(remember),
                ),
            )
            cnx.commit()
            success = True
        except Exception as e:
            print("Error", str(e))
            cnx.rollback()

        cursor.close()
        cnx.close()

        return success



