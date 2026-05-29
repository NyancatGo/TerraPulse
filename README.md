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

> [!IMPORTANT]
> **🔐 Sisteme Giriş Bilgileri (Varsayılan)**
> Uygulamaya giriş yapabilmek için aşağıdaki yetkilendirilmiş hesapları kullanabilirsiniz:
> - **Yönetici (Admin):** Kullanıcı Adı: `admin` &nbsp;&nbsp;|&nbsp;&nbsp; Şifre: `admin123`
> - **Analist (User):** Kullanıcı Adı: `analist` &nbsp;&nbsp;|&nbsp;&nbsp; Şifre: `user123`

---

## 📑 İçindekiler
- [🎯 Proje Amacı](#-proje-amacı)
- [✨ Temel Özellikler](#-temel-özellikler)
- [🛠️ Teknoloji Yığını ve Mimari](#️-teknoloji-yığını-ve-mimari)
- [📊 Matematiksel Modelleme](#-matematiksel-modelleme)
- [📂 Proje Yapısı](#-proje-yapısı)
- [🚀 Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
- [📦 Kendi Exe Dosyanızı Oluşturma (Build Rehberi)](#-kendi-exe-dosyanızı-oluşturma-build-rehberi)
- [💻 Geliştirici Rehberi (Projeyi Nasıl Geliştirebilirsiniz?)](#-geliştirici-rehberi-projeyi-nasıl-geliştirebilirsiniz)
- [👥 Hedef Kitle](#-hedef-kitle)

---

## 🎯 Proje Amacı

**TerraPulse**, Türkiye'nin sismik geçmişini modern veri bilimi teknikleriyle analiz eden, masaüstü tabanlı güçlü bir karar destek ve araştırma yazılımıdır. AFAD, Kandilli Rasathanesi ve USGS gibi global/yerel kaynaklardan elde edilen karmaşık sismik verileri anlamlandırarak interaktif haritalara, istatistiksel grafiklere ve olasılık modellerine dönüştürür.

Amacımız, tarihsel verileri kullanarak **"Hangi bölge ne kadar risk altında?"** sorusuna bilimsel ve görsel bir yanıt sunmaktır.

---

## ✨ Temel Özellikler

* **🔐 Güvenli Erişim Sistemi:** Yetkilendirilmiş kullanıcı girişi (Farklı sistem yetkilerine sahip Admin ve Analist rolleri).
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

## 📦 Kendi Exe Dosyanızı Oluşturma (Build Rehberi)

Kaynak kodda (örneğin yeni bir analiz sekmesi veya veri filtresi) değişiklik yaptıktan sonra uygulamayı son kullanıcılar için yeniden paketlemek isterseniz, proje kök dizininde bulunan **özel derleme betiğini** kullanmalısınız.

### Adım Adım Build İşlemi:

1. **Önkoşullar:** Geliştirme ortamınızda `pyinstaller` modülünün kurulu olduğundan emin olun (`pip install pyinstaller`).
2. **Derlemeyi Başlatma:** Proje ana dizininde (TerraPulse klasörü) terminali açın ve aşağıdaki komutu çalıştırın:
   ```bash
   python build_exe.py
   ```
3. **Arka Planda Neler Oluyor?**
   - Betik, önce eski `build/` ve `dist/` klasörlerini otomatik temizler.
   - `terrapulse.spec` dosyasını okuyarak uygulamanın derinlemesine analizini yapar.
   - *PyQtWebEngine* (Chromium tarayıcı motoru), *Folium* harita şablonları (`branca` dahil) ve *fpdf* (PDF kütüphanesi) gibi karmaşık bileşenlerin tüm gizli bağımlılıklarını (hidden imports) güvenle toplar.
   - Uygulama içi yolları ayarlayan `paths.py` sistemi sayesinde, veritabanı ve asset klasörleri exe ortamına (frozen environment) uygun şekilde paketlenir.
4. **Sonuç:** İşlem bittiğinde (bilgisayar hızına göre yaklaşık 2-5 dakika sürebilir), `dist/TerraPulse/` dizininde **kullanıma hazır `TerraPulse.exe`** dosyanız oluşacaktır.
5. **Dağıtım (Deployment):** Uygulamayı başka bir bilgisayara taşımak isterseniz sadece `.exe` dosyasını değil, `dist/TerraPulse/` klasörünü **tamamen bir zip dosyası haline getirip** paylaşmalısınız (çünkü yanındaki `_internal` klasörü kritik sistem dosyalarını barındırır).

---

## 💻 Geliştirici Rehberi (Projeyi Nasıl Geliştirebilirsiniz?)

TerraPulse, ekip çalışmasına uygun, modüler ve genişletilebilir bir MVC-benzeri mimariyle tasarlanmıştır. Projeye yeni özellikler eklemek veya katkıda bulunmak isteyen geliştiriciler için temel kurallar:

### 1. Yeni Bir Arayüz (UI) Sekmesi Eklemek
Kullanıcı arayüzüne ait tüm sınıflar `src/ui/` dizinindedir. Ana pencere `main_window.py` üzerinden sekmeli (`QTabWidget`) bir yapı sunar.
- Yeni bir görselleştirme paneli eklemek için `src/ui/` altında yeni bir Python dosyası/sınıfı oluşturun (Örn: `fault_lines_tab.py`).
- Oluşturduğunuz sınıfı `main_window.py` içindeki `init_ui()` metodunda tab listesine import edip dahil edin.

### 2. Veritabanı İşlemleri (SQLite3)
Projeye ait tüm veri iletişimi **sadece** `src/database/db_manager.py` üzerinden yürütülür.
- Ham verileri çekmek veya yeni sorgular yazmak için `db_manager.py` içine yepyeni fonksiyonlar (Örn: `get_earthquakes_by_region()`) ekleyin.
- Arayüz (`ui`) sınıflarının içinden doğrudan SQL sorgusu (`SELECT * FROM...`) **yazmayın**. Veritabanı sorgularını her zaman Manager sınıfına yaptırın; bu kodun spagetti olmasını engeller.

### 3. Dinamik Harita ve Grafik Üretimi
- Haritalama algoritmaları ve folium kodları `src/visualization/map_engine.py` modülü içerisindedir. Yeni bir görselleştirme katmanı (Örn: `MarkerCluster`) eklemek isterseniz bu dosyaya yeni bir fonksiyon tanımlayın.
- Dosya yolları (şablonlar, geojson'lar, html'ler) okuyacaksanız **MUTLAKA** `src/utils/paths.py` içindeki `get_resource_path()` metodunu kullanın. Bunu yapmazsanız kodunuz IDE üzerinde çalışır ancak uygulamayı `.exe` yaptığınızda uygulama anında çöker!

### 4. Kod Düzeni ve Standartlar
- Projede okunabilirliği artırmak için Fonksiyon İmzaları (Type Hinting) kullanımı tavsiye edilir (Örn: `def calculate_risk(magnitude: float) -> dict:`).
- Büyük veri setleri üzerinde (örneğin 100 bin deprem kaydı) analiz yaparken standart Python `for/while` döngüleri yerine, performans için daima **Pandas vektörizasyon** tekniklerini kullanın.

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
