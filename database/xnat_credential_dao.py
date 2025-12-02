from database.DB_connect import DBConnect
from database.xnat_credential_dto import XnatCredentialDto


class XnatCredentialDao:
    @staticmethod
    def get_all_credentials():
        cnx = DBConnect.get_connection()
        if cnx is None:
            print("Connection Error")
            return None
        else:
            result = []
            cursor = cnx.cursor()
            query = """SELECT address, username, password, remember
                    FROM xnat_credentials"""

            cursor.execute(query)
            for row in cursor:
                result.append(
                    XnatCredentialDto(row["address"], row["username"],
                                      row["password"], bool(row["remember"]))
                )

            cursor.close()
            cnx.close()

            return result

    @staticmethod
    def get_remembered_credential():
        cnx = DBConnect.get_connection()
        if cnx is None:
            print("Connection Error")
            return None
        else:
            result = None
            cursor = cnx.cursor()
            query = """SELECT address, username, password, remember
                    FROM xnat_credentials
                    WHERE remember = 1
                    ORDER BY rowid DESC
                    LIMIT 1"""

            cursor.execute(query)
            row = cursor.fetchone()

            if row:
                result = XnatCredentialDto(
                    row["address"],
                    row["username"],
                    row["password"],
                    bool(row["remember"]),
                )

            cursor.close()
            cnx.close()

            return result

    @staticmethod
    def clear_credentials():
        cnx = DBConnect.get_connection()
        if cnx is None:
            print("Connection Error")
            return None
        else:
            query_delete_rows = "DELETE FROM xnat_credentials"

            query_reset_ai = """DELETE FROM sqlite_sequence
                                WHERE name=?"""
            cursor = cnx.cursor()
            success = False

            try:
                cursor.execute(query_delete_rows)
                cursor.execute(query_reset_ai, ("xnat_credentials",))
                cnx.commit()
                success = True
            except Exception as e:
                print("Error", str(e))
                cnx.rollback()

            cursor.close()
            cnx.close()

            return success

    @staticmethod
    def replace_credentials(address, username, password, remember):
        cnx = DBConnect.get_connection()
        if cnx is None:
            print("Connection Error")
            return None
        else:
            query_insert = """INSERT INTO xnat_credentials
                                (address, username, password, remember)
                                VALUES (?,?,?,?)"""
            cursor = cnx.cursor()
            success = False

            try:
                cursor.execute("DELETE FROM xnat_credentials")
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name=?",
                    ("xnat_credentials",),
                )
                if remember:
                    cnx.execute(
                        query_insert,
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