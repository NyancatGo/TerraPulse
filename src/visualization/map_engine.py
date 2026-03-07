"""
TerraPulse Map Engine
Folium tabanlı interaktif harita oluşturma modülü - Hafta 6: Gelişmiş Katmanlar
"""
import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import os
import json


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
        tiles="OpenStreetMap",
        attr="TerraPulse - Sismik Veri Analizi"
    )
    return turkey_map


def get_color_by_depth(depth):
    """Derinliğe göre renk döndürür"""
    if depth is None or depth == 'N/A':
        return '#808080'  # Gri
    
    depth = float(depth)
    if depth < 10:
        return '#FF0000'  # Kırmızı - Sığ (en tehlikeli)
    elif depth < 30:
        return '#FF6600'  # Turuncu
    elif depth < 70:
        return '#FFB300'  # Sarı-Turuncu
    elif depth < 150:
        return '#FFFF00'  # Sarı
    elif depth < 300:
        return '#90EE90'  # Açık Yeşil
    else:
        return '#006400'  # Koyu Yeşil - Derin


def get_radius_by_magnitude(magnitude):
    """Büyüklüğe göre marker boyutu döndürür"""
    if magnitude >= 7.0:
        return 16
    elif magnitude >= 6.0:
        return 12
    elif magnitude >= 5.0:
        return 9
    elif magnitude >= 4.0:
        return 6
    else:
        return 4


def add_earthquake_markers(map_obj, df, use_clustering=True):
    """
    Deprem markerlarını haritaya ekler - Gelişmiş stil
    
    Args:
        map_obj: Folium Map objesi
        df: Deprem verileri içeren DataFrame
        use_clustering: MarkerCluster kullan
    """
    # MarkerCluster
    if use_clustering:
        marker_cluster = MarkerCluster(
            name="🔴 Deprem Noktaları",
            overlay=True,
            control=True,
            show=True
        )
    else:
        marker_cluster = folium.FeatureGroup(name="🔴 Deprem Noktaları", show=True)
    
    # Performans limiti
    max_markers = min(len(df), 5000)
    
    for idx, row in df.head(max_markers).iterrows():
        magnitude = row.get("magnitude", 0)
        depth = row.get("depth", 'N/A')
        place = row.get('place', 'Bilinmiyor')
        time = row.get('time', 'N/A')
        
        # Derinliğe göre renk, büyüklüğe göre boyut
        color = get_color_by_depth(depth)
        radius = get_radius_by_magnitude(magnitude)
        
        # Zengin popup içeriği
        popup_html = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">🌍 Deprem Bilgisi</h4>
            <hr style="margin: 5px 0;">
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>📊 Büyüklük:</b></td><td><span style="color: red; font-size: 16px; font-weight: bold;">{magnitude}</span></td></tr>
                <tr><td><b>📍 Konum:</b></td><td>{place}</td></tr>
                <tr><td><b>🕳️ Derinlik:</b></td><td>{depth} km</td></tr>
                <tr><td><b>📅 Tarih:</b></td><td>{time[:19] if len(str(time)) > 19 else time}</td></tr>
                <tr><td><b>📌 Koordinat:</b></td><td>{row['latitude']:.3f}, {row['longitude']:.3f}</td></tr>
            </table>
        </div>
        """
        
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color='black',
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"<b>Mag {magnitude}</b> | {depth} km derinlik"
        ).add_to(marker_cluster)
    
    marker_cluster.add_to(map_obj)
    
    if len(df) > max_markers:
        print(f"⚡ Performans: {len(df)} depremin ilk {max_markers} tanesi gösteriliyor")


def add_heatmap(map_obj, df, name="🔥 Yoğunluk Haritası", max_points=3000):
    """
    Deprem yoğunluk haritası ekler
    
    Args:
        map_obj: Folium Map objesi
        df: Deprem verileri DataFrame
        name: Katman ismi
        max_points: Maksimum nokta sayısı
    """
    sample_size = min(len(df), max_points)
    df_sample = df.sample(n=sample_size) if len(df) > max_points else df
    
    heat_data = [
        [row["latitude"], row["longitude"], row.get("magnitude", 1)]
        for _, row in df_sample.iterrows()
    ]
    
    heat_group = folium.FeatureGroup(name=name, show=False, overlay=True, control=True)
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


def add_fault_lines(map_obj, geojson_path=None):
    """
    Türkiye fay hatlarını haritaya ekler
    
    Args:
        map_obj: Folium Map objesi
        geojson_path: GeoJSON dosya yolu
    """
    if geojson_path is None:
        # Varsayılan yol
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        geojson_path = os.path.join(base_dir, "data", "geo", "turkey_fault_lines.geojson")
    
    if not os.path.exists(geojson_path):
        print(f"⚠️ Fay hatları dosyası bulunamadı: {geojson_path}")
        return
    
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            fault_data = json.load(f)
        
        # Fay hatları katmanı
        fault_layer = folium.FeatureGroup(name="⚠️ Fay Hatları", show=True, overlay=True, control=True)
        
        # Her fay hattı için stil ve popup
        for feature in fault_data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            # Risk seviyesine göre renk ve kalınlık
            risk = props.get('risk', 'Orta')
            if risk == 'Çok Yüksek':
                color = '#8B0000'  # Koyu Kırmızı
                weight = 4
            elif risk == 'Yüksek':
                color = '#FF4500'  # Turuncu-Kırmızı
                weight = 3
            else:
                color = '#FFA500'  # Turuncu
                weight = 2
            
            # Popup içeriği
            popup_html = f"""
            <div style="font-family: Arial; width: 280px;">
                <h4 style="margin: 0 0 10px 0; color: #8B0000;">⚠️ {props['name']}</h4>
                <hr style="margin: 5px 0;">
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b>⚡ Risk Seviyesi:</b></td><td><span style="color: red; font-weight: bold;">{risk}</span></td></tr>
                    <tr><td><b>📏 Uzunluk:</b></td><td>{props.get('length_km', 'N/A')} km</td></tr>
                    <tr><td><b>🔧 Tip:</b></td><td>{props.get('type', 'N/A')}</td></tr>
                    <tr><td colspan="2"><br><i>{props.get('description', '')}</i></td></tr>
                </table>
            </div>
            """
            
            folium.PolyLine(
                locations=[[lat, lon] for lon, lat in coords],
                color=color,
                weight=weight,
                opacity=0.8,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=props['name']
            ).add_to(fault_layer)
        
        fault_layer.add_to(map_obj)
        print(f"✅ {len(fault_data['features'])} fay hattı eklendi")
        
    except Exception as e:
        print(f"❌ Fay hatları yükleme hatası: {e}")


def add_legend(map_obj):
    """
    Haritaya kompakt açıklama kutusu (legend) ekler
    """
    legend_html = """
    <div style="position: fixed; 
                bottom: 20px; right: 15px; width: 190px; height: auto;
                background-color: rgba(255, 255, 255, 0.95); z-index:9999; font-size:9px;
                border:1.5px solid #999; border-radius: 6px; padding: 6px;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);">
        
        <h4 style="margin: 0 0 4px 0; text-align: center; color: #333; font-size: 11px;">
            🗺️ Açıklama
        </h4>
        <hr style="margin: 3px 0;">
        
        <p style="margin: 3px 0 1px 0; font-weight: bold; font-size: 9px;">Büyüklük:</p>
        <p style="margin: 1px 0 1px 12px; line-height: 1.3;"><span style="font-size: 6px;">⬤</span> <4.0 · <span style="font-size: 9px;">⬤</span> 4-5 · <span style="font-size: 12px;">⬤</span> 5-6 · <span style="font-size: 15px;">⬤</span> >6</p>
        
        <p style="margin: 4px 0 1px 0; font-weight: bold; font-size: 9px;">Derinlik:</p>
        <p style="margin: 1px 0 1px 12px; line-height: 1.4;">
            <span style="color: #FF0000;">⬤</span> <10km · 
            <span style="color: #FF6600;">⬤</span> 10-30 · 
            <span style="color: #FFB300;">⬤</span> 30-70<br>
            <span style="margin-left: 12px;"><span style="color: #FFFF00;">⬤</span> 70-150 · 
            <span style="color: #006400;">⬤</span> >300km</span>
        </p>
        
        <p style="margin: 4px 0 1px 0; font-weight: bold; font-size: 9px;">Fay Hatları:</p>
        <p style="margin: 1px 0 1px 12px; line-height: 1.3;">
            <span style="color: #8B0000; font-weight: bold;">━</span> Çok Yüksek · 
            <span style="color: #FF4500; font-weight: bold;">━</span> Yüksek · 
            <span style="color: #FFA500; font-weight: bold;">━</span> Orta
        </p>
        
        <p style="margin: 3px 0 0 0; text-align: center; font-size: 7px; color: #888;">
            TerraPulse © 2026
        </p>
    </div>
    """
    
    map_obj.get_root().html.add_child(folium.Element(legend_html))


def create_earthquake_map(df, output_path="map.html"):
    """
    Tüm özellikleri içeren profesyonel deprem haritası oluşturur
    
    Args:
        df: Deprem verileri DataFrame
        output_path: Kaydedilecek HTML dosya yolu
    
    Returns:
        Oluşturulan HTML dosya yolu
    """
    # Temel harita oluştur
    earthquake_map = create_base_map()
    
    # Deprem verisi varsa katmanları ekle
    if not df.empty:
        # 1. Deprem Markerları (cluster ile)
        add_earthquake_markers(earthquake_map, df, use_clustering=True)
        
        # 2. Heatmap
        add_heatmap(earthquake_map, df)
        
        # 3. Fay Hatları
        add_fault_lines(earthquake_map)
        
        # 4. Legend (Açıklama)
        add_legend(earthquake_map)
    
    # Katman kontrolü ekle (sağ üst)
    folium.LayerControl(
        position='topright',
        collapsed=False,
        autoZIndex=True
    ).add_to(earthquake_map)
    
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
