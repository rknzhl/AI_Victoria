import sqlite3

from config import DATABASE_PATH as PATH

class DataBase:

    def __init__(self, params):
        self.params = params
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        query = "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY"

        for param, default_value in params.items():
            query += f", {param} INTEGER DEFAULT {default_value}"

        query += ")"

        c.execute(query)

        conn.commit()
        conn.close()

    def add_user(self, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        placeholders = ', '.join(['?'] * len(self.params))
        query = f"INSERT OR IGNORE INTO users (username, {', '.join(self.params.keys())}) VALUES (?, {placeholders})"
        values = [username] + list(self.params.values())

        c.execute(query, values)

        conn.commit()
        conn.close()

    def set_args(self, user, args):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        update_fields = ', '.join([f"{key} = ?" for key in args.keys()])
        query = f"UPDATE users SET {update_fields} WHERE username = ?"
        values = list(args.values()) + [user]

        c.execute(query, values)

        conn.commit()
        conn.close()


    def get_args(self, user):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        query = f"SELECT {', '.join(self.params.keys())} FROM users WHERE username = ?"

        c.execute(query, (user,))
        result = c.fetchone()

        conn.close()

        if result is None:
            return {}

        args = {param: bool(value) for param, value in zip(self.params.keys(), result)}

        return args