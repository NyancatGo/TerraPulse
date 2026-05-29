import sqlite3
import pandas as pd
import os
import sys
import math
import hashlib

from data_processing.data_cleaner import DataCleaner
from utils.paths import get_resource_path, get_db_path, get_data_dir


REGION_BOUNDS = {
    "Marmara": {"min_lat": 39.0, "max_lat": 42.2, "min_lon": 25.8, "max_lon": 31.2},
    "Ege": {"min_lat": 36.8, "max_lat": 39.5, "min_lon": 25.8, "max_lon": 30.0},
    "Akdeniz": {"min_lat": 36.0, "max_lat": 38.5, "min_lon": 29.5, "max_lon": 37.0},
    "İç Anadolu": {"min_lat": 37.5, "max_lat": 40.5, "min_lon": 30.5, "max_lon": 36.5},
    "Karadeniz": {"min_lat": 40.0, "max_lat": 42.5, "min_lon": 31.0, "max_lon": 41.5},
    "Doğu Anadolu": {"min_lat": 37.0, "max_lat": 40.5, "min_lon": 37.0, "max_lon": 44.5},
    "Güneydoğu Anadolu": {"min_lat": 36.5, "max_lat": 38.5, "min_lon": 37.0, "max_lon": 43.0},
}

DEFAULT_USERS = (
    ("admin", "admin123", "admin"),
    ("analist", "user123", "user"),
)


def _get_risk_level(probability):
    """Poisson olasılığına göre risk sınıfı döndürür."""
    if probability >= 0.60:
        return "Çok Yüksek"
    if probability >= 0.40:
        return "Yüksek"
    if probability >= 0.20:
        return "Orta"
    if probability >= 0.10:
        return "Düşük"
    return "Çok Düşük"


def hash_password(password: str) -> str:
    """Girilen parolayi SHA-256 ile ozetler."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _get_selected_region_bounds(*regions):
    """Secilen bolgeler icin tekrarsiz koordinat sinirlarini dondurur."""
    selected_bounds = []
    seen_regions = set()

    for region in regions:
        if region in REGION_BOUNDS and region not in seen_regions:
            selected_bounds.append(REGION_BOUNDS[region])
            seen_regions.add(region)

    return selected_bounds


def _build_region_bounds_filter(bounds_list):
    """SQLite icin bolge koordinat filtrelerini ve parametrelerini hazirlar."""
    conditions = []
    params = []

    for bounds in bounds_list:
        conditions.append("(latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?)")
        params.extend([
            bounds["min_lat"],
            bounds["max_lat"],
            bounds["min_lon"],
            bounds["max_lon"],
        ])

    return conditions, params


class DBManager:
    def __init__(self, db_path: str = None):
        # Merkezi yol yonetimi uzerinden yazilabilir DB konumunu al
        self.db_path = db_path or get_db_path()
        
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
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
            )
            '''
        )
        cursor.executemany(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            [(username, hash_password(password), role) for username, password, role in DEFAULT_USERS],
        )
        self.conn.commit()

    def load_dataframe_to_db(self, df: pd.DataFrame, table_name: str = "earthquakes"):
        """Pandas DataFrame'indeki temizlenmiş verileri SQLite tablosuna aktarır."""
        if df.empty:
            print("Aktarılacak veri bulunamadı!")
            return
            
        # DataFrame içerisindeki veriyi SQLite'a ekle
        df.to_sql(table_name, self.conn, if_exists='replace', index=False)
        print(f"Süper! Toplam {len(df)} deprem verisi başarılı bir şekilde '{table_name}' tablosuruna (terrapulse.db) yüklendi.")

    def fetch_earthquakes(self, min_mag=0.0, max_mag=10.0, start_year=None, end_year=None, region1=None, region2=None):
        """
        Filtrelenmiş deprem verilerini SQLite'tan çeker
        
        Args:
            min_mag: Minimum büyüklük
            max_mag: Maximum büyüklük
            start_year: Başlangıç yılı (opsiyonel)
            end_year: Bitiş yılı (opsiyonel)
            region1: Bölge 1 ismi (opsiyonel)
            region2: Bölge 2 ismi (opsiyonel)
        
        Returns:
            Pandas DataFrame
        """
        query = "SELECT * FROM earthquakes WHERE magnitude >= ? AND magnitude <= ?"
        params = [min_mag, max_mag]
        
        # Tarih filtresi varsa ekle
        if start_year and end_year:
            query += " AND strftime('%Y', time) BETWEEN ? AND ?"
            params.extend([str(start_year), str(end_year)])
            
        # Secilen bolgeler icin metin yerine koordinat sinirlariyla filtrele
        selected_bounds = _get_selected_region_bounds(region1, region2)
        if selected_bounds:
            region_conditions, region_params = _build_region_bounds_filter(selected_bounds)
            query += " AND (" + " OR ".join(region_conditions) + ")"
            params.extend(region_params)
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            print(f"📊 Veritabanından {len(df)} deprem çekildi (Mag: {min_mag:.1f}-{max_mag:.1f})")
            return df
        except Exception as e:
            print(f"❌ Veritabanı sorgu hatası: {e}")
            return pd.DataFrame()

    def calculate_poisson_risk_scores(self, min_mag=5.0, start_year=None, end_year=None, forecast_years=1, region_filter=None):
        """
        Bölgelere göre Poisson tabanlı deprem risk skorlarını hesaplar.

        Args:
            min_mag: Risk hesabına dahil edilecek minimum büyüklük
            start_year: Analiz başlangıç yılı
            end_year: Analiz bitiş yılı
            forecast_years: Tahmin ufku (yıl)
            region_filter: Sadece secilen bolgenin riskini hesaplamak icin bolge adi

        Returns:
            Bölge bazlı skor listesi
        """
        if forecast_years <= 0:
            forecast_years = 1

        if start_year is None or end_year is None:
            start_year, end_year = self.get_date_range()

        if start_year > end_year:
            start_year, end_year = end_year, start_year

        analysis_years = max(1, (end_year - start_year) + 1)
        df = self.fetch_earthquakes(
            min_mag=min_mag,
            max_mag=10.0,
            start_year=start_year,
            end_year=end_year,
            region1=region_filter if region_filter in REGION_BOUNDS else None,
        )

        scores = []
        latitudes = pd.Series(dtype=float)
        longitudes = pd.Series(dtype=float)
        if not df.empty and {"latitude", "longitude"}.issubset(df.columns):
            latitudes = pd.to_numeric(df["latitude"], errors="coerce")
            longitudes = pd.to_numeric(df["longitude"], errors="coerce")

        target_regions = REGION_BOUNDS.items()
        if region_filter in REGION_BOUNDS:
            target_regions = [(region_filter, REGION_BOUNDS[region_filter])]

        for region, bounds in target_regions:
            if latitudes.empty or longitudes.empty:
                event_count = 0
            else:
                region_mask = (
                    (latitudes >= bounds["min_lat"]) &
                    (latitudes <= bounds["max_lat"]) &
                    (longitudes >= bounds["min_lon"]) &
                    (longitudes <= bounds["max_lon"])
                )
                event_count = int(region_mask.sum())

            annual_rate = event_count / analysis_years
            probability = 1 - math.exp(-annual_rate * forecast_years)
            recurrence_years = (1 / annual_rate) if annual_rate > 0 else None

            scores.append({
                "region": region,
                "event_count": event_count,
                "analysis_years": analysis_years,
                "annual_rate": annual_rate,
                "forecast_years": forecast_years,
                "probability": probability,
                "risk_score": probability * 100,
                "risk_level": _get_risk_level(probability),
                "recurrence_years": recurrence_years,
                "min_magnitude": min_mag,
                "start_year": start_year,
                "end_year": end_year,
            })

        return sorted(scores, key=lambda row: row["risk_score"], reverse=True)
    
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

    def authenticate_user(self, username: str, password: str):
        """Kullanici adini ve parolayi dogrulayip rol bilgisini dondurur."""
        normalized_username = (username or "").strip()
        normalized_password = password or ""

        if not normalized_username or not normalized_password:
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = ?",
                (normalized_username,),
            )
            row = cursor.fetchone()
        except Exception as exc:
            print(f"❌ Kullanici dogrulama hatasi: {exc}")
            return None

        if not row:
            return None

        user_id, stored_username, stored_hash, role = row
        if stored_hash != hash_password(normalized_password):
            return None

        return {
            "id": user_id,
            "username": stored_username,
            "role": role,
        }

    def get_user_count(self) -> int:
        """users tablosundaki kayit sayisini dondurur."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return int(cursor.fetchone()[0])
        except Exception:
            return 0

def build_database():
    """Tüm süreci başlatan yardımcı fonksiyon."""
    csv_path = get_resource_path(os.path.join("data", "raw", "earthquakes.csv"))
    cleaner = DataCleaner(csv_path)
    
    df = cleaner.process_data()
    db = DBManager()
    
    if not df.empty:
        db.load_dataframe_to_db(df)
    db.close()

def ensure_database_exists():
    """Veritabanı yoksa oluşturur, varsa kontrol eder"""
    db_path = get_db_path()  # paths.py varsayilan DB'yi otomatik kopyalar
    
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
