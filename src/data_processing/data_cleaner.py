import pandas as pd
import os

class DataCleaner:
    def __init__(self, raw_data_path: str = "data/raw/earthquakes.csv"):
        self.raw_data_path = raw_data_path
    
    def process_data(self) -> pd.DataFrame:
        """
        USGS veya benzeri CSV deprem verisini okur ve temizler.
        Orijinal Sütunlar: Time,Magnitude,Place,Latitude,Longitude,Depth
        """
        print(f"Veri okunuyor: {self.raw_data_path}")
        if not os.path.exists(self.raw_data_path):
            print("HATA: CSV dosyası bulunamadı!")
            return pd.DataFrame()
            
        df = pd.DataFrame()
        try:
            # CSV dosyasını Pandas ile oku
            df = pd.read_csv(self.raw_data_path)
            
            # Eksik (NaN) değere sahip olan bozuk satırları temizle
            df.dropna(inplace=True)
            
            # Sütun isimlerini küçük harflere çevir (SQLite uyumluluğu için)
            df.columns = [col.lower() for col in df.columns]
            
            print(f"Veri analizi ve temizliği tamamlandı. Toplam {len(df)} adet deprem kaydı işlendi.")
            return df
            
        except Exception as e:
            print(f"Bilinmeyen bir veri okuma hatası oluştu: {e}")
            return df

if __name__ == "__main__":
    cleaner = DataCleaner()
    temizlenmis_df = cleaner.process_data()
    print(temizlenmis_df.head(3))
