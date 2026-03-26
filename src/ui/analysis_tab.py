import sys
import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QApplication
)
from PyQt6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AnalysisTab(QWidget):
    """
    Kullanıcının verilerine göre Matplotlib grafiklerini PyQt6 arayüzüne 
    native olarak gömen (embedding) AnalysisTab sınıfı.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_modern_styling()

    def init_ui(self):
        # 1. Ana Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 2. Esnek Yerleşim için Splitter
        # Dikey (Vertical) splitter, üstte zaman serisini, altta yan yana iki grafiği tutacak.
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ÜST BÖLÜM: Zaman Serisi (Line Chart)
        self.fig_time = Figure()
        self.canvas_time = FigureCanvas(self.fig_time)
        self.ax_time = self.fig_time.add_subplot(111)
        
        # ALT BÖLÜM: Histogram ve Scatter Plot için yatay splitter
        self.bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Alt Sol: Büyüklük Histogramı
        self.fig_hist = Figure()
        self.canvas_hist = FigureCanvas(self.fig_hist)
        self.ax_hist = self.fig_hist.add_subplot(111)
        
        # Alt Sağ: Derinlik vs Büyüklük
        self.fig_scatter = Figure()
        self.canvas_scatter = FigureCanvas(self.fig_scatter)
        self.ax_scatter = self.fig_scatter.add_subplot(111)

        # Alt grafikleri yatay splitter'a ekleme
        self.bottom_splitter.addWidget(self.canvas_hist)
        self.bottom_splitter.addWidget(self.canvas_scatter)
        
        # Splitter içine canvas'ları ekleme
        self.main_splitter.addWidget(self.canvas_time)
        self.main_splitter.addWidget(self.bottom_splitter)
        
        # Yükseklik Oranları Ayarlama
        self.main_splitter.setSizes([350, 250])
        # Genişlik Oranları (Alt kısım için)
        self.bottom_splitter.setSizes([1, 1])

        main_layout.addWidget(self.main_splitter)

    def apply_modern_styling(self):
        """
        Matplotlib'in genel varsayılanlarını, uygulamanın
        karanlık/modern arayüzüne veya seçilen fontlara uydurmak içindir.
        """
        # Sistem fontunu ayarla (Windows için Segoe UI tercih edilebilir)
        matplotlib.rc('font', family='Segoe UI', size=10)
        
        # Tüm ana arka planları tamamen şeffaf yapıyoruz
        # Arayüzünüzün kendi arka plan rengi varsa arkadan kendini gösterecektir.
        for fig in [self.fig_time, self.fig_hist, self.fig_scatter]:
            fig.patch.set_facecolor('#00000000') 
            
    def apply_axes_styling(self, ax, title, xlabel, ylabel):
        """
        Her bir matplotlib eksenine (Axes) modern görünüm kazandırır.
        """
        # Eksene arka plan rengini şeffaf yapma
        ax.set_facecolor('#00000000')
        
        # Izgara (Grid) ayarları: Kesik kesik çizgi, düşük opaklık
        ax.grid(True, linestyle='--', alpha=0.3, color='#808080')
        
        # Çerçeveleri (Spines) temizleme ve düşük opaklık verme
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_alpha(0.2)
        ax.spines['bottom'].set_alpha(0.2)
        
        # Eksen metinlerinin renkleri ve boyutları
        ax.tick_params(axis='both', colors='#666666', labelsize=9)
        
        # Başlık ve Etiket ayarları
        ax.set_title(title, pad=10, fontsize=12, fontweight='bold', color='#333333')
        ax.set_xlabel(xlabel, fontsize=10, color='#444444')
        ax.set_ylabel(ylabel, fontsize=10, color='#444444')

    def update_charts(self, filtered_df: pd.DataFrame):
        """
        Dışarıdan gelen Pandas DataFrame ile grafikleri canlandırır.
        Eski verileri ax.clear() ile siler, yenisiyle çizer ve draw() ile günceller.
        """
        # 1. Eski çizimleri temizle
        self.ax_time.clear()
        self.ax_hist.clear()
        self.ax_scatter.clear()

        if filtered_df is None or filtered_df.empty:
            print("❌ Graph Warning: filtered_df boş veya None geldi.")
            self.ax_time.text(0.5, 0.5, 'Veri Bulunamadı', ha='center', va='center', color='gray')
            self.ax_hist.text(0.5, 0.5, 'Veri Bulunamadı', ha='center', va='center', color='gray')
            self.ax_scatter.text(0.5, 0.5, 'Veri Bulunamadı', ha='center', va='center', color='gray')
        else:
            try:
                df = filtered_df.copy()
                print(f"✅ Gelen Veri Sütunları: {df.columns.tolist()}")

                # Eğer SQLite sütun isimleriniz 'time' yerine 'date' ise vs. otomatik eşleyin
                # db_manager'ı incelediğimde sütunlar: ['id', 'time', 'magnitude', 'place', 'latitude', 'longitude', 'depth'] şeklinde.
                # Sizin yazdığınız kodlarda 'time' olarak döndüğü gözlemlendi. Biz bunu 'date' bekliyoruz, o yüzden bir eşleştirme (mapping) yapıyoruz.
                if 'time' in df.columns and 'date' not in df.columns:
                    df = df.rename(columns={'time': 'date'})
                    print("🔄 Sütun eşleştirildi: 'time' -> 'date'")
                
                # --- ZAMAN SERİSİ (Zamana Göre Sismik Büyüklük) ---
                if 'date' in df.columns and 'magnitude' in df.columns:
                    if not pd.api.types.is_datetime64_any_dtype(df['date']):
                        df['date'] = pd.to_datetime(df['date'])
                    
                    df_sorted = df.sort_values('date')
                    self.ax_time.plot(df_sorted['date'], df_sorted['magnitude'], 
                                     color='#0078D7', marker='o', markersize=3, linewidth=1, alpha=0.6)
                    self.apply_axes_styling(self.ax_time, "Zamana Göre Sismik Aktivite", "Tarih", "Büyüklük (Mw)")
                else:
                    print("⚠️ Eksik Sütun: Zaman serisi (date, magnitude) çizilemedi.")
                
                # --- HİSTOGRAM (Deprem Büyüklük Dağılımı Frekansı) ---
                if 'magnitude' in df.columns:
                    self.ax_hist.hist(df['magnitude'], bins=20, color='#FF8C00', edgecolor='white', alpha=0.8)
                    self.apply_axes_styling(self.ax_hist, "Büyüklük Frekansı", "Büyüklük (Mw)", "Deprem Sayısı")
                else:
                    print("⚠️ Eksik Sütun: Histogram (magnitude) çizilemedi.")
                    
                # --- SCATTER PLOT (Derinlik vs. Büyüklük İlişkisi) ---
                if 'magnitude' in df.columns and 'depth' in df.columns:
                    self.ax_scatter.scatter(df['magnitude'], df['depth'], 
                                            alpha=0.6, c=df['magnitude'], cmap='viridis', edgecolors='none')
                    
                    # Derinlik Y ekseninde normalde aşağı doğru iner
                    self.ax_scatter.invert_yaxis()
                    self.apply_axes_styling(self.ax_scatter, "Derinlik - Büyüklük İlişkisi", "Büyüklük (Mw)", "Derinlik (km)")
                else:
                    print("⚠️ Eksik Sütun: Scatter Plot (magnitude, depth) çizilemedi.")

            except Exception as e:
                print(f"❌ Matplotlib Çizim Hatası: {e}")
                import traceback
                traceback.print_exc()

        # 3. Yanaşmaları Otomatik Hizala (Aksi halde yazılar kenarlara sıkışır)
        self.fig_time.tight_layout()
        self.fig_hist.tight_layout()
        self.fig_scatter.tight_layout()

        # 4. Çizilenleri Ekrana Yansıt!
        self.canvas_time.draw()
        self.canvas_hist.draw()
        self.canvas_scatter.draw()

# ----------------------------------------------------
# DUMMY (TEST) ÇALIŞTIRMA BLOKU
# Sadece bu dosya çalıştırıldığında test verisi üretip ekranda gösterir.
# ----------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. 100 günlük sahte sismik veri üret
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=100, freq='D')
    magnitudes = np.random.normal(loc=3.5, scale=1.0, size=100) # Ortalama 3.5 büyüklük
    depths = np.random.uniform(5.0, 35.0, size=100) # 5-35 km arası derinlik
    
    dummy_df = pd.DataFrame({
        'date': dates,
        'magnitude': magnitudes,
        'depth': depths
    })
    
    # Sınıfı oluştur ve dummy dataframe ile besle
    window = AnalysisTab()
    window.resize(900, 700)
    window.setWindowTitle("TerraPulse - Karşılaştırmalı Analiz Testi")
    
    # Siyahımtırak modern arka planı (Koyu mod) simüle etmek için test pencere rengi
    window.setStyleSheet("background-color: #FAFAFA;") 
    
    # (Eğer temanız karanlık moddaysa #FAFAFA yerine #1E1E1E deneyip apply_axes_styling color'larını açık renk yapmalısınız)
    
    window.update_charts(dummy_df)
    window.show()
    
    sys.exit(app.exec())
