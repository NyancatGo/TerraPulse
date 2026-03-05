"""
TerraPulse Map Engine
Folium tabanlı interaktif harita oluşturma modülü
"""
import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import os


def create_base_map(center=[39.0, 35.0], zoom=6):
    """
    Temel Türkiye haritası oluşturur
    
    Args:
        center: Harita merkezi [lat, lon]
        zoom: Başlangıç zoom seviyesi
    
    Returns:
        folium.Map objesi
    """
    turkey_map = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )
    return turkey_map


def add_earthquake_markers(map_obj, df, use_clustering=True):
    """
    Deprem markerlarını haritaya ekler (MarkerCluster ile optimize)
    
    Args:
        map_obj: Folium Map objesi
        df: Deprem verileri içeren DataFrame (latitude, longitude, magnitude kolonları gerekli)
        use_clustering: MarkerCluster kullan (performans için önerilir)
    """
    # MarkerCluster ile performans optimizasyonu
    if use_clustering:
        marker_cluster = MarkerCluster(
            name="Deprem Noktaları",
            overlay=True,
            control=True
        )
    else:
        marker_cluster = folium.FeatureGroup(name="Deprem Noktaları")
    
    # Performans için maksimum marker sayısını sınırla
    max_markers = min(len(df), 5000)
    
    for idx, row in df.head(max_markers).iterrows():
        # Büyüklüğe göre renk seçimi
        magnitude = row.get("magnitude", 0)
        if magnitude >= 5.0:
            color = "red"
            icon_color = "red"
            radius = 8
        elif magnitude >= 4.0:
            color = "orange" 
            icon_color = "orange"
            radius = 6
        else:
            color = "yellow"
            icon_color = "lightblue"
            radius = 4
        
        # Popup içeriği
        popup_html = f"""
        <b>Büyüklük:</b> {magnitude}<br>
        <b>Yer:</b> {row.get('place', 'Bilinmiyor')}<br>
        <b>Derinlik:</b> {row.get('depth', 'N/A')} km<br>
        <b>Tarih:</b> {row.get('time', 'N/A')}
        """
        
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Mag: {magnitude}"
        ).add_to(marker_cluster)
    
    marker_cluster.add_to(map_obj)
    
    # Bilgi mesajı
    if len(df) > max_markers:
        print(f"⚡ Performans: {len(df)} depremin ilk {max_markers} tanesi gösteriliyor")


def add_heatmap(map_obj, df, name="Isı Haritası", max_points=3000):
    """
    Deprem yoğunluk haritası ekler (optimize edilmiş)
    
    Args:
        map_obj: Folium Map objesi
        df: Deprem verileri içeren DataFrame
        name: Katman ismi
        max_points: Maksimum nokta sayısı (performans için)
    """
    # Performans için veri sayısını sınırla
    sample_size = min(len(df), max_points)
    df_sample = df.sample(n=sample_size) if len(df) > max_points else df
    
    # Heatmap için veri hazırlama
    heat_data = [
        [row["latitude"], row["longitude"], row.get("magnitude", 1)]
        for _, row in df_sample.iterrows()
    ]
    
    # Heatmap katmanı oluştur
    heat_group = folium.FeatureGroup(name=name)
    HeatMap(
        heat_data,
        min_opacity=0.2,
        max_opacity=0.6,
        radius=12,
        blur=15,
        max_zoom=10,
        gradient={0.4: 'blue', 0.6: 'lime', 0.8: 'orange', 1.0: 'red'}
    ).add_to(heat_group)
    
    heat_group.add_to(map_obj)
    
    if len(df) > max_points:
        print(f"⚡ Heatmap: {len(df)} depremin {max_points} örneği kullanıldı")


def create_earthquake_map(df, output_path="map.html"):
    """
    Tüm özellikleri içeren tam deprem haritası oluşturur
    
    Args:
        df: Deprem verileri DataFrame
        output_path: Kaydedilecek HTML dosya yolu
    
    Returns:
        Oluşturulan HTML dosya yolu
    """
    # Temel harita oluştur
    earthquake_map = create_base_map()
    
    # Deprem markerları ekle
    if not df.empty:
        add_earthquake_markers(earthquake_map, df)
        add_heatmap(earthquake_map, df)
    
    # Katman kontrolü ekle
    folium.LayerControl(position='topright', collapsed=False).add_to(earthquake_map)
    
    # Haritayı kaydet
    output_path = os.path.abspath(output_path)
    earthquake_map.save(output_path)
    print(f"✅ Harita oluşturuldu: {output_path}")
    
    return output_path


def filter_earthquakes(df, min_magnitude=0.0, max_magnitude=10.0, 
                       start_date=None, end_date=None):
    """
    Deprem verilerini filtreler
    
    Args:
        df: Deprem DataFrame
        min_magnitude: Minimum büyüklük
        max_magnitude: Maximum büyüklük
        start_date: Başlangıç tarihi (opsiyonel)
        end_date: Bitiş tarihi (opsiyonel)
    
    Returns:
        Filtrelenmiş DataFrame
    """
    filtered = df.copy()
    
    # Büyüklük filtresi
    filtered = filtered[
        (filtered['magnitude'] >= min_magnitude) & 
        (filtered['magnitude'] <= max_magnitude)
    ]
    
    # Tarih filtresi (eğer varsa)
    if start_date and 'time' in filtered.columns:
        filtered = filtered[filtered['time'] >= start_date]
    if end_date and 'time' in filtered.columns:
        filtered = filtered[filtered['time'] <= end_date]
    
    return filtered
