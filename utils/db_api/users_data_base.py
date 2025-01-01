import sqlite3


class DatabaseUsers:
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

    def create_table_users(self):
        sql = """
        CREATE TABLE Users (
            user_id INT UNIQUE,
            user_name TEXT,
            user_first_name TEXT,
            user_last_name TEXT
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

    def add_user(self, user_id: int, user_name: str, user_first_name: str, user_last_name: str):
        sql = """
        INSERT INTO Users(user_id, user_name, user_first_name, user_last_name) 
        VALUES(?, ?, ?, ?)
        """
        self.execute(sql, parameters=(user_id, user_name, user_first_name, user_last_name), commit=True)

    def update_user_info(self, user_id, **kwargs):
        sql = "UPDATE Users SET "
        sql, parameters = self.formatArgs(sql, kwargs)
        sql += " WHERE user_id = ?;"
        parameters += (user_id,)
        return self.execute(sql, parameters=parameters, commit=True)

    def select_user(self, user_id, **kwargs):
        sql = f"SELECT * FROM Users WHERE user_id = '{user_id}'"
        sql, parameters = self.formatArgs(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def select_all_users(self):
        sql = f"SELECT * FROM Users"
        return self.execute(sql, fetchall=True)


# def logger(statement):
#     print(f"""
# _____________________________________________________
# Executing:
# {statement}
# _____________________________________________________
# """)

# ALTER TABLE Users ADD user_wallet INT DEFAULT 0