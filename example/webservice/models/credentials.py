from utils.db import Db


class Credentials(Db):
    def __init__(self):
        Db.__init__(self)
        self.table = 'credentials'
        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def get(self):
        self.cursor.execute("SELECT * FROM `credentials`")
        return self.cursor.fetchone()

    def set(self, token, subsperdayremain):
        self.cursor.execute("DELETE FROM `credentials`")
        self.cursor.execute(
            "INSERT INTO `credentials` "
            "VALUES(:token, :subsperdayremain)",
            {"token": token, "subsperdayremain": subsperdayremain }
        )
        self.conn.commit()
