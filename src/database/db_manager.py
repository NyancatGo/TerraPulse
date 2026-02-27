import sqlite3
import pandas as pd
import os

class DBManager:
    def __init__(self, db_path: str = "data/processed/terrapulse.db"):
        self.db_path = db_path
        self._create_db_dir()
        self.conn = self._connect()
        self._init_tables()

    def _create_db_dir(self):
        """Veritabanı dizini yoksa oluştur."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self):
        """Veritabanına bağlanır."""
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        """Tabloları oluşturur (eğer yoksa)."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earthquakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                magnitude REAL NOT NULL,
                depth REAL,
                location TEXT
            )
        ''')
        self.conn.commit()

    def load_dataframe_to_db(self, df: pd.DataFrame, table_name: str = "earthquakes"):
        """Pandas DataFrame'i SQLite'a aktarır."""
        df.to_sql(table_name, self.conn, if_exists='append', index=False)
        print(f"Data successfully loaded to {table_name} table.")

    def close(self):
        """Bağlantıyı kapatır."""
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    db = DBManager()
    print("Database manager initialized.")
    db.close()
