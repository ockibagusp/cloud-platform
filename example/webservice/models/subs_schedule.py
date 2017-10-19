from utils.db import Db


class SubsScedule(Db):
    def __init__(self):
        Db.__init__(self)
        self.table = "subs_schedule"
        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def getall(self):
        self.cursor.execute("SELECT * FROM `%s`" % self.table)
        return self.cursor.fetchall()

    def getbyid(self, subs_id):
        self.cursor.execute(
            "SELECT * FROM `%s` WHERE id=:id" % self.table,
            {"id": subs_id}
        )
        return self.cursor.fetchone()

    def edit(self, subs_id, time):
        self.cursor.execute(
            "UPDATE `%s` SET time=:time WHERE id=:id" % self.table,
            {"id": subs_id, "time": str(time)}
        )
        self.conn.commit()

    def delete(self, subs_id):
        self.cursor.execute(
            "DELETE FROM `%s` WHERE id=:id" % self.table,
            {"id": subs_id}
        )
        self.conn.commit()

    def deleteall(self):
        self.cursor.execute("DELETE FROM `%s`" % self.table)
        self.conn.commit()

    def create(self, time):
        # TODO check
        self.cursor.execute(
            "INSERT INTO `%s` (`time`)"
            "VALUES(:time)" % self.table,
            {"time": str(time)}
        )
        self.conn.commit()