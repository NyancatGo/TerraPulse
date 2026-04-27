import sqlite3
import pandas as pd
import os
import sys
import math
import hashlib

# DataCleaner'ı bulabilmesi için import yollarını düzeltiyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processing.data_cleaner import DataCleaner


REGION_CITIES = {
    "Marmara": ["İstanbul", "Edirne", "Kırklareli", "Tekirdağ", "Çanakkale", "Kocaeli", "Yalova", "Sakarya", "Bilecik", "Bursa", "Balıkesir"],
    "Ege": ["İzmir", "Manisa", "Aydın", "Denizli", "Muğla", "Afyonkarahisar", "Kütahya", "Uşak"],
    "Akdeniz": ["Antalya", "Isparta", "Burdur", "Adana", "Mersin", "Osmaniye", "Hatay", "Kahramanmaraş"],
    "İç Anadolu": ["Ankara", "Konya", "Kayseri", "Eskişehir", "Sivas", "Kırıkkale", "Aksaray", "Karaman", "Kırşehir", "Niğde", "Nevşehir", "Yozgat", "Çankırı"],
    "Karadeniz": ["Trabzon", "Samsun", "Ordu", "Giresun", "Rize", "Artvin", "Zonguldak", "Sinop", "Bartın", "Karabük", "Kastamonu", "Çorum", "Amasya", "Tokat", "Gümüşhane", "Bayburt", "Bolu", "Düzce"],
    "Doğu Anadolu": ["Erzurum", "Erzincan", "Kars", "Ağrı", "Ardahan", "Iğdır", "Van", "Hakkari", "Bitlis", "Muş", "Bingöl", "Tunceli", "Elazığ", "Malatya"],
    "Güneydoğu Anadolu": ["Gaziantep", "Diyarbakır", "Şanlıurfa", "Batman", "Adıyaman", "Mardin", "Siirt", "Şırnak", "Kilis"]
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
            
        # Seçilen bölgelerdeki şehirleri tek listede topla
        target_cities = []
        if region1 and region1 in REGION_CITIES:
            target_cities.extend(REGION_CITIES[region1])
        if region2 and region2 in REGION_CITIES:
            # Seçilen ikinci bölge birinci ile aynı değilse (veya set ile duplicate temizle)
            if region2 != region1:
                target_cities.extend(REGION_CITIES[region2])
                
        # Eğer kullanıcının seçimine yönelik şehirler bulunduysa SQL AND (.. OR ..) filtresini ekle
        if target_cities:
            city_conditions = ["place LIKE ?" for _ in target_cities]
            # Tüm şehirlere özel parametreler
            params.extend([f"%{city}%" for city in target_cities])
            
            # (place LIKE '%Muğla%' OR place LIKE '%İzmir%' OR ...) yapısı
            query += " AND (" + " OR ".join(city_conditions) + ")"
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            print(f"📊 Veritabanından {len(df)} deprem çekildi (Mag: {min_mag:.1f}-{max_mag:.1f})")
            return df
        except Exception as e:
            print(f"❌ Veritabanı sorgu hatası: {e}")
            return pd.DataFrame()

    def calculate_poisson_risk_scores(self, min_mag=5.0, start_year=None, end_year=None, forecast_years=1):
        """
        Bölgelere göre Poisson tabanlı deprem risk skorlarını hesaplar.

        Args:
            min_mag: Risk hesabına dahil edilecek minimum büyüklük
            start_year: Analiz başlangıç yılı
            end_year: Analiz bitiş yılı
            forecast_years: Tahmin ufku (yıl)

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
            end_year=end_year
        )

        scores = []
        place_series = pd.Series(dtype=str)
        if not df.empty and 'place' in df.columns:
            place_series = df['place'].fillna('').astype(str)

        for region, cities in REGION_CITIES.items():
            if place_series.empty:
                event_count = 0
            else:
                region_mask = pd.Series(False, index=place_series.index)
                for city in cities:
                    region_mask = region_mask | place_series.str.contains(city, case=False, regex=False)
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
