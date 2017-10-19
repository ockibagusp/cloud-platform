import os
import sqlite3


class Db:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        is_new = False
        if not os.path.isfile("storage.db"):
            print('create new database storage.db')
            is_new = True
        self.conn = sqlite3.connect(r"storage.db")
        self.cursor = self.conn.cursor()
        if is_new:
            self.migrate()

    def disconnect(self):
        self.cursor.close()
        self.conn.close()

    # generate new tables
    def migrate(self):
        print('generate initial tables')
        sql_query_credentials = "CREATE TABLE IF NOT EXISTS `credentials` (" \
            "`token`	TEXT," \
            "`subsperdayremain`	INTEGER DEFAULT 0" \
            ")"
        sql_query_subs_scedule = "CREATE TABLE IF NOT EXISTS `subs_schedule` (" \
            "`id`	INTEGER PRIMARY KEY AUTOINCREMENT," \
            "`time`	TEXT)"
        self.cursor.execute(sql_query_credentials)
        self.cursor.execute(sql_query_subs_scedule)
        self.conn.commit()
