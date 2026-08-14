import sqlite3
import random

class DB_Manager:

    def __init__(self, database):
         self.conn = sqlite3.connect(database)
         self.cursor = self.conn.cursor()

    def add_folder(self, folder_name):
        self.cursor.execute(
            "INSERT INTO FOLDER (name) VALUES (?)",
            (folder_name,)
        )
        self.conn.commit()

    def get_folders(self):
         self.cursor.execute("SELECT * FROM FOLDER")
         return self.cursor.fetchall()

    def add_card(self, folder_id, question, answer):
        self.cursor.execute(
            """
            INSERT INTO CARD (folder_id, question, answer)
            VALUES (?, ?, ?)
            """,
            (folder_id, question, answer)
        )

        self.conn.commit()

    def get_cards(self, folder_id):
        self.cursor.execute(
            "SELECT * FROM CARD WHERE folder_id = ?",
            (folder_id,)
        )
        return self.cursor.fetchall()

    def get_random_card(self,folder_id):
        cards = self.get_cards(folder_id)

        if not cards:
            return None

        return random.choice(cards)

