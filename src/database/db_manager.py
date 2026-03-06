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
        # Tablo yoksa oluştur (DROP yapma!)
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

    def fetch_earthquakes(self, min_mag=0.0, max_mag=10.0, start_year=None, end_year=None):
        """
        Filtrelenmiş deprem verilerini SQLite'tan çeker
        
        Args:
            min_mag: Minimum büyüklük
            max_mag: Maximum büyüklük
            start_year: Başlangıç yılı (opsiyonel)
            end_year: Bitiş yılı (opsiyonel)
        
        Returns:
            Pandas DataFrame
        """
        query = "SELECT * FROM earthquakes WHERE magnitude >= ? AND magnitude <= ?"
        params = [min_mag, max_mag]
        
        # Tarih filtresi varsa ekle
        if start_year and end_year:
            query += " AND strftime('%Y', time) BETWEEN ? AND ?"
            params.extend([str(start_year), str(end_year)])
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            print(f"📊 Veritabanından {len(df)} deprem çekildi (Mag: {min_mag:.1f}-{max_mag:.1f})")
            return df
        except Exception as e:
            print(f"❌ Veritabanı sorgu hatası: {e}")
            return pd.DataFrame()
    
    def get_date_range(self):
        """Veritabanındaki en eski ve en yeni deprem tarihlerini döndürür"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT MIN(time), MAX(time) FROM earthquakes")
            min_date, max_date = cursor.fetchone()
            
            if min_date and max_date:
                # Yıl olarak döndür
                min_year = int(min_date[:4]) if len(min_date) >= 4 else 2000
                max_year = int(max_date[:4]) if len(max_date) >= 4 else 2025
                return min_year, max_year
            return 2000, 2025
        except:
            return 2000, 2025
    
    def get_magnitude_range(self):
        """Veritabanındaki min ve max magnitude değerlerini döndürür"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT MIN(magnitude), MAX(magnitude) FROM earthquakes")
            min_mag, max_mag = cursor.fetchone()
            return (min_mag or 0.0), (max_mag or 10.0)
        except:
            return 0.0, 10.0
    
    def get_earthquake_count(self, min_mag=0.0, start_year=None, end_year=None):
        """Filtrelenmiş deprem sayısını döndürür"""
        try:
            query = "SELECT COUNT(*) FROM earthquakes WHERE magnitude >= ?"
            params = [min_mag]
            
            if start_year and end_year:
                query += " AND strftime('%Y', time) BETWEEN ? AND ?"
                params.extend([str(start_year), str(end_year)])
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count
        except:
            return 0
    
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

def ensure_database_exists():
    """Veritabanı yoksa oluşturur, varsa kontrol eder"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "data/processed/terrapulse.db")
    
    # Veritabanı yoksa oluştur
    if not os.path.exists(db_path):
        print("📦 Veritabanı bulunamadı, oluşturuluyor...")
        build_database()
        return True
    
    # Veritabanı var ama boş mu kontrol et
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM earthquakes")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            print("📦 Veritabanı boş, veri yükleniyor...")
            # Veritabanını sil ve yeniden oluştur
            os.remove(db_path)
            build_database()
            return True
        else:
            print(f"✅ Veritabanı mevcut: {count} deprem kaydı")
            return True
    except Exception as e:
        print(f"📦 Veritabanı hatası ({e}), yeniden oluşturuluyor...")
        if os.path.exists(db_path):
            os.remove(db_path)
        build_database()
        return True

if __name__ == "__main__":
    build_database()
