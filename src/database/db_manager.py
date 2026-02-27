import sqlite3
import pandas as pd
import os
import sys

# DataCleaner'ı bulabilmesi için import yollarını düzeltiyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processing.data_cleaner import DataCleaner

class DBManager:
    def __init__(self, db_path: str = "data/processed/terrapulse.db"):
        # Projenin kök dizininden referans almak için mutlak yola çevir
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, db_path)
        
        self._create_db_dir()
        self.conn = self._connect()
        self._init_tables()

    def _create_db_dir(self):
        """Veritabanı dizini yoksa oluştur."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self):
        """SQLite veritabanına bağlanır."""
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        """Tabloları USGS veri formatına göre oluşturur."""
        cursor = self.conn.cursor()
        # Eğer mock tablo varsa eski formatı temizleyip yenisini oluştur
        cursor.execute("DROP TABLE IF EXISTS earthquakes")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earthquakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL,
                magnitude REAL NOT NULL,
                place TEXT,
                latitude REAL,
                longitude REAL,
                depth REAL
            )
        ''')
        self.conn.commit()

    def load_dataframe_to_db(self, df: pd.DataFrame, table_name: str = "earthquakes"):
        """Pandas DataFrame'indeki temizlenmiş verileri SQLite tablosuna aktarır."""
        if df.empty:
            print("Aktarılacak veri bulunamadı!")
            return
            
        # DataFrame içerisindeki veriyi SQLite'a ekle
        df.to_sql(table_name, self.conn, if_exists='replace', index=False)
        print(f"Süper! Toplam {len(df)} deprem verisi başarılı bir şekilde '{table_name}' tablosuruna (terrapulse.db) yüklendi.")

    def close(self):
        """Bağlantıyı kapatır."""
        if self.conn:
            self.conn.close()

def build_database():
    """Tüm süreci başlatan yardımcı fonksiyon."""
    # DataCleaner'ın düzgün adres okuması için yolu düzelt
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cleaner = DataCleaner(os.path.join(base_dir, "data/raw/earthquakes.csv"))
    
    df = cleaner.process_data()
    db = DBManager()
    
    if not df.empty:
        db.load_dataframe_to_db(df)
    db.close()

if __name__ == "__main__":
    build_database()
