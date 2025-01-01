import sqlite3


class DatabaseMedia:
    def __init__(self, path_to_db="allData.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        with sqlite3.connect(self.path_to_db) as connection:
            # connection.set_trace_callback(logger)
            cursor = connection.cursor()
            data = None
            cursor.execute(sql, parameters)
            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
        return data

    def create_table_media(self):
        sql = """
        CREATE TABLE Media (
            media_url TEXT UNIQUE,
            media_id TEXT,
            media_type TEXT
            );
        """
        self.execute(sql, commit=True)

    @staticmethod
    def formatArgs(sql, parameters: dict):
        if len(parameters) == 1:
            bat = " AND "
        else:
            bat = ", "
        sql += bat.join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_media(self, media_url: str, media_id: str, media_type: str):
        sql = """
            INSERT INTO Media (media_url, media_id, media_type) VALUES (?, ?, ?)
            """
        self.execute(sql, parameters=(media_url, media_id, media_type), commit=True)

    def update_media_info(self, media_url, **kwargs):
        sql = "UPDATE Media SET "
        sql, parameters = self.formatArgs(sql, kwargs)
        sql += " WHERE media_url = ?;"
        parameters += (media_url,)
        return self.execute(sql, parameters=parameters, commit=True)

    def select_media_by_url(self, **kwargs):
        sql = "SELECT * FROM Media WHERE "
        sql, parameters = self.formatArgs(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def delete_media_by_url(self, media_url: int):
        sql = "DELETE FROM Media WHERE media_url = ?;"
        self.execute(sql, parameters=(media_url,), commit=True)


# def logger(statement):
#     print(f"""
# _____________________________________________________
# Executing:
# {statement}
# _____________________________________________________
# """)