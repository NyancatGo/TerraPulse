<div align="center">
  <h1>🌍 TerraPulse</h1>
  <p><b>Gelişmiş Türkiye Sismik Veri Analizi ve İstatistiksel Risk Değerlendirme Sistemi</b></p>

  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
  [![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
  [![Folium](https://img.shields.io/badge/Map-Folium-orange.svg)](https://python-visualization.github.io/folium/)
  [![SQLite](https://img.shields.io/badge/DB-SQLite-lightgrey.svg)](https://sqlite.org/)
  [![PyInstaller](https://img.shields.io/badge/Build-PyInstaller-red.svg)](https://pyinstaller.org/)
  [![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
</div>

---

## 📑 İçindekiler
- [🎯 Proje Amacı](#-proje-amacı)
- [✨ Temel Özellikler](#-temel-özellikler)
- [🛠️ Teknoloji Yığını ve Mimari](#️-teknoloji-yığını-ve-mimari)
- [📊 Matematiksel Modelleme](#-matematiksel-modelleme)
- [📂 Proje Yapısı](#-proje-yapısı)
- [🚀 Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
- [📦 Kendi Exe Dosyanızı Oluşturma](#-kendi-exe-dosyanızı-oluşturma)
- [👥 Hedef Kitle](#-hedef-kitle)

---

## 🎯 Proje Amacı

**TerraPulse**, Türkiye'nin sismik geçmişini modern veri bilimi teknikleriyle analiz eden, masaüstü tabanlı güçlü bir karar destek ve araştırma yazılımıdır. AFAD, Kandilli Rasathanesi ve USGS gibi global/yerel kaynaklardan elde edilen karmaşık sismik verileri anlamlandırarak interaktif haritalara, istatistiksel grafiklere ve olasılık modellerine dönüştürür.

Amacımız, tarihsel verileri kullanarak **"Hangi bölge ne kadar risk altında?"** sorusuna bilimsel ve görsel bir yanıt sunmaktır.

---

## ✨ Temel Özellikler

* **🔐 Güvenli Erişim Sistemi:** Yetkilendirilmiş kullanıcı girişi (Varsayılan kullanıcı: `admin` / Şifre: `admin`).
* **🗺️ İnteraktif Folium Haritaları:** PyQtWebEngine içerisine gömülü, dinamik olarak güncellenen fay hattı gösterimleri, deprem kümelenmeleri ve yoğunluk (Heatmap) haritaları.
* **⚡ Çevrimdışı Performans:** Verilerin yerel **SQLite** veritabanında saklanması sayesinde internet bağlantısı olmadan ultra hızlı filtreleme ve sorgulama.
* **📈 İstatistiksel Analiz Modülleri:** Tarihsel deprem frekans analizleri, derinlik-büyüklük ilişkileri ve trend grafikleri (Matplotlib entegrasyonu).
* **🎲 Poisson Risk Modellemesi:** Belirli büyüklükteki depremlerin X yıl içerisinde tekrarlanma olasılıklarının bilimsel olarak hesaplanması.
* **📄 Otomatik PDF Raporlama:** Yapılan analizlerin, harita görüntülerinin ve grafiklerin tek tıkla kurumsal şablonda (FPDF) dışa aktarılması.
* **🚀 Taşınabilirlik (Standalone Executable):** Hiçbir Python veya kütüphane kurulumu gerektirmeyen, bağımsız `.exe` formatı. Uygulama verileri exe'nin yanında güvenle saklanır.

---

## 🛠️ Teknoloji Yığını ve Mimari

TerraPulse, modern Python kütüphanelerinin gücünü masaüstü performansıyla birleştirir:

| Katman | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Arayüz (GUI)** | `PyQt6` & `QtWebEngine` | Gelişmiş, sekmeli masaüstü iskeleti ve dahili tarayıcı motoru. |
| **Veri İşleme** | `Pandas` & `NumPy` | Büyük sismik veri setlerinin temizlenmesi ve manipülasyonu. |
| **Görselleştirme**| `Folium`, `Matplotlib`, `branca` | İnteraktif HTML tabanlı haritalar ve istatistiksel grafikler. |
| **Veritabanı** | `SQLite3` | Hafif, yerel ve ilişkisel veri depolama. |
| **Raporlama** | `fpdf2` | Dinamik veri tabloları ve grafiklerle otomatik PDF üretimi. |
| **Paketleme** | `PyInstaller` | Bağımlılıkların çözümlenmesi ve Windows Exe derlemesi. |

---

## 📊 Matematiksel Modelleme

TerraPulse, deprem riskini değerlendirmek için **Poisson Dağılım Modeli**'ni kullanır. Bu model, belirli bir zaman aralığında rastgele gerçekleşen nadir olayların (büyük depremler gibi) olasılığını hesaplamak için global sismolojide standart olarak kabul edilir.

> **P(x) = (e^-λ * λ^x) / x!**
> *(λ: Belirli bir bölge için yıllık ortalama deprem beklentisi)*

Yazılım, kullanıcının seçtiği bir fay zonundaki tarihsel verileri tarayarak `λ` değerini otomatik hesaplar ve gelecek 10, 50 veya 100 yıl için istatistiksel risk yüzdelerini çıkarır.

---

## 📂 Proje Yapısı

```text
TerraPulse/
├── data/                  # Kaynak veri dosyaları
│   ├── geo/               # Fay hatları (GeoJSON)
│   ├── processed/         # İşlenmiş veritabanı şablonu (SQLite)
│   └── raw/               # Ham deprem verileri (CSV)
├── sql/                   # Veritabanı kurulum scriptleri
├── src/                   # Kaynak Kod (Core)
│   ├── data_processing/   # Veri temizleme ve manipülasyon mantığı
│   ├── database/          # SQLite bağlantı ve sorgu yöneticileri
│   ├── reporting/         # PDF rapor üretim modülü
│   ├── ui/                # PyQt6 arayüz bileşenleri (Pencereler, Tablar, Bileşenler)
│   ├── utils/             # Ortak yardımcı fonksiyonlar (örn: paths.py)
│   └── visualization/     # Folium harita ve Matplotlib grafik motorları
├── build_exe.py           # Otomatik PyInstaller paketleme betiği
├── terrapulse.spec        # PyInstaller konfigürasyon dosyası
├── requirements.txt       # Python bağımlılık listesi
└── README.md              # Proje dokümantasyonu
```

---

## 🚀 Kurulum ve Çalıştırma

Kullanım amacınıza göre iki farklı yöntemle TerraPulse'u çalıştırabilirsiniz.

### Seçenek 1: Bağımsız Çalıştırılabilir (Exe) Kullanımı (Önerilen)
Yazılımı kullanmak için bilgisayarınızda Python kurulu olmasına gerek yoktur.

1. Kaynak kod içerisindeki `dist/TerraPulse/` klasörünü bilgisayarınıza kopyalayın.
2. Klasör içindeki **`TerraPulse.exe`** dosyasına çift tıklayın.
3. *Not: Uygulama ilk çalıştırıldığında kendi veritabanını ve önbelleğini oluşturmak için exe'nin bulunduğu dizinde `TerraPulse_Data` adında bir klasör oluşturacaktır. Lütfen yazılımı okuma/yazma izni olan bir klasörde çalıştırın (Örn: Masaüstü veya Belgeler).*

### Seçenek 2: Kaynak Koddan Çalıştırma (Geliştiriciler İçin)

1. **Depoyu Klonlayın:**
   ```bash
   git clone https://github.com/NyancatGo/TerraPulse.git
   cd TerraPulse
   ```

2. **Sanal Ortam (Virtual Environment) Oluşturun (Opsiyonel):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows için
   ```

3. **Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı Başlatın:**
   ```bash
   # PYTHONPATH ayarlanarak çalıştırılır
   $env:PYTHONPATH="src"    # Windows PowerShell
   python src/app.py
   ```

---

## 📦 Kendi Exe Dosyanızı Oluşturma

Kaynak kodda değişiklik yaptıktan sonra uygulamayı yeniden paketlemek isterseniz, proje kök dizininde bulunan özel derleme betiğini kullanabilirsiniz:

```bash
python build_exe.py
```
Bu betik arka planda `terrapulse.spec` dosyasını okuyarak, PyQtWebEngine, Folium şablonları, fpdf ve diğer tüm kütüphaneleri eksiksiz bir şekilde derler. İşlem bittiğinde yeni exe dosyanız (yaklaşık 24 MB) `dist/TerraPulse/` dizininde hazır olacaktır.

---

## 👥 Hedef Kitle

- 🎓 **Akademisyenler ve Sismologlar:** Tarihsel deprem verilerinin mekansal ve istatistiksel analizi.
- 📚 **Öğrenciler:** Tez, araştırma ve veri madenciliği projeleri için interaktif bir referans kaynağı.
- 🏢 **Yerel Yönetimler ve Plancılar:** Kentsel dönüşüm, risk haritalandırması ve zemin etüdü için makro ölçekte veri tabanlı raporlama.

---

<div align="center">
  <i>"Depreme karşı en güçlü silahımız, onu veriyle anlamaktır."</i><br><br>
  <b>TerraPulse Development Team</b>
</div>
