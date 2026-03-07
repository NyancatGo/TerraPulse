<div align="center">
  <br>
  <h1>🌍 TerraPulse</h1>
  <p><b>Türkiye Sismik Veri Analizi ve İstatistiksel Risk Değerlendirme Sistemi</b></p>
  <br>
</div>

## 🎯 Proje Amacı
**TerraPulse**, Türkiye'nin sismik geçmişini bilimsel yöntemlerle analiz eden ve elde edilen bulguları interaktif haritalar ile istatistiksel modellerle görselleştiren bir masaüstü karar destek yazılımıdır. Karmaşık sismik veri setlerini (USGS, AFAD, Kandilli) işleyerek; *"Hangi bölge ne kadar deprem riski taşıyor?"* sorusuna tarihsel veriler ve olasılık modelleriyle yanıt vermeyi hedefler.

## 👥 Hedef Kitle
- **🎓 Akademisyenler ve Araştırmacılar:** Tarihsel deprem verilerinin mekansal ve istatistiksel (Poisson dağılımı vb.) analizi.
- **📚 Üniversite Öğrencileri:** Tez, akademik araştırma ve veri analizi projeleri için güvenilir referans kaynağı.
- **🏢 Şehir Plancıları ve Yerel Yönetimler:** Kentsel dönüşüm, risk değerlendirmesi ve zemin etüdü ön çalışmaları için veri tabanlı raporlama.

## ⚡ Temel Özellikler
- **Sekmeli (Tab-Based) Arayüz:** "Harita & Filtreleme", "Karşılaştırmalı Analiz" ve "Risk Skorlama" modülleri.
- **Çevrimdışı Çalışma:** Verilerin yerel SQLite veritabanında önbelleklenmesi (caching) ile internetsiz, ultra hızlı filtreleme.
- **İnteraktif Folium Haritaları:** Isı haritaları (Heatmap), fay hatları ve dinamik nokta kümelenmeleri.
- **İstatistiksel Risk Modelleme:** Belirli büyüklükteki depremlerin tekrarlanma periyotlarının hesaplanması (*Poisson Dağılımı*).
- **PDF Raporlama:** Yapılan analizlerin tek tıkla kurumsal şablonda dışa aktarılması.

## 🛠️ Teknoloji Yığını
| Alan | Teknoloji | Amaç |
| --- | --- | --- |
| **Dil** | Python | Çekirdek dil |
| **Arayüz (GUI)** | PyQt6 & PyQtWebEngine | Sekmeli masaüstü pencere iskeleti ve tarayıcı motoru |
| **Veritabanı** | SQLite | Çevrimdışı ultra hızlı filtreleme |
| **Veri Analizi** | Pandas | Keşifsel Veri Analizi (EDA) ve veri temizliği |
| **Harita** | Folium | İnteraktif haritalar ve ısı haritaları |
| **Görselleştirme**| Matplotlib | Karşılaştırmalı analiz grafikleri |

> **Veri Kaynakları:** USGS Küresel Deprem Veritabanı, Kandilli Rasathanesi, AFAD Sismik Ağ Verileri.

## 🚀 Kurulum (Local Development)
Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/kullaniciadi/terrapulse.git
   cd terrapulse
   ```

2. **Gerekli bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Uygulamayı başlatın:**
   ```bash
   # src klasörünü PYTHONPATH'e ekleyerek çalıştırın (Windows powershell için)
   $env:PYTHONPATH="src"
   python src/app.py
   ```

---
<div align="center">
  <i>"Depreme karşı en güçlü silahımız, onu anlamaktır."</i>
</div>
