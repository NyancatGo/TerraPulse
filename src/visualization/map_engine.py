"""
TerraPulse Map Engine
Folium tabanli interaktif harita olusturma modulu.
"""

import json
import os

import folium
import pandas as pd
from folium.plugins import FastMarkerCluster, HeatMap


MAX_DETAIL_MARKERS = 260
MAX_HEAT_POINTS = 1200


def create_base_map(center=[39.0, 35.0], zoom=6):
    """
    Temel Turkiye haritasi olusturur.
    """
    turkey_map = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB positron",
        attr="TerraPulse - Sismik Veri Analizi",
        prefer_canvas=True,
        control_scale=True,
    )
    return turkey_map


def get_color_by_depth(depth):
    """Derinlige gore renk dondurur."""
    if depth is None or depth == "N/A":
        return "#808080"

    depth = float(depth)
    if depth < 10:
        return "#FF0000"
    if depth < 30:
        return "#FF6600"
    if depth < 70:
        return "#FFB300"
    if depth < 150:
        return "#FFFF00"
    if depth < 300:
        return "#90EE90"
    return "#006400"


def get_radius_by_magnitude(magnitude):
    """Buyukluge gore marker boyutu dondurur."""
    if magnitude >= 7.0:
        return 12
    if magnitude >= 6.0:
        return 10
    if magnitude >= 5.0:
        return 7
    if magnitude >= 4.0:
        return 5
    return 4


def _prepare_marker_subset(df: pd.DataFrame, max_markers: int = MAX_DETAIL_MARKERS) -> pd.DataFrame:
    """
    Harita performansi icin marker alt kumesi hazirlar.

    Buyuk depremler mutlaka korunur, kalan kapasite ise temsili ornekleme ile doldurulur.
    """
    if len(df) <= max_markers:
        return df

    ranked = df.sort_values(["magnitude", "time"], ascending=[False, False], na_position="last")
    return ranked.head(max_markers)


def _popup_html(row) -> str:
    """Daha hafif popup html uret."""
    time_value = getattr(row, "time", "N/A")
    time_text = str(time_value)[:19] if time_value is not None else "N/A"
    place = getattr(row, "place", "Bilinmiyor")
    magnitude = getattr(row, "magnitude", "N/A")
    depth = getattr(row, "depth", "N/A")
    latitude = getattr(row, "latitude", 0.0)
    longitude = getattr(row, "longitude", 0.0)

    return f"""
    <div style="font-family: Arial, sans-serif; width: 215px; font-size: 12px;">
        <div style="font-weight: 700; font-size: 14px; margin-bottom: 6px;">Deprem Bilgisi</div>
        <div><b>Buyukluk:</b> {magnitude}</div>
        <div><b>Konum:</b> {place}</div>
        <div><b>Derinlik:</b> {depth} km</div>
        <div><b>Tarih:</b> {time_text}</div>
        <div><b>Koordinat:</b> {latitude:.3f}, {longitude:.3f}</div>
    </div>
    """


def add_earthquake_markers(map_obj, df, use_clustering=True):
    """
    Deprem markerlarini haritaya ekler.
    """
    cluster_points = [
        [row.latitude, row.longitude, float(getattr(row, "magnitude", 0.0))]
        for row in df.itertuples(index=False)
    ]

    cluster_callback = """
    function (row) {
        const magnitude = row[2];
        const radius = magnitude >= 7 ? 7 : magnitude >= 6 ? 6 : magnitude >= 5 ? 5 : 4;
        const color = magnitude >= 6 ? '#ef4444' : magnitude >= 5 ? '#f59e0b' : '#38bdf8';
        return L.circleMarker(new L.LatLng(row[0], row[1]), {
            radius: radius,
            color: '#0f172a',
            weight: 1,
            fillColor: color,
            fillOpacity: 0.62
        });
    }
    """

    fast_cluster = FastMarkerCluster(
        data=cluster_points,
        name="Deprem Noktalari",
        overlay=True,
        control=True,
        show=True,
        callback=cluster_callback,
    )
    fast_cluster.add_to(map_obj)

    detail_group = folium.FeatureGroup(name="Detayli Buyuk Depremler", show=True)
    detail_df = _prepare_marker_subset(df, max_markers=MAX_DETAIL_MARKERS)

    for row in detail_df.itertuples(index=False):
        magnitude = getattr(row, "magnitude", 0)
        depth = getattr(row, "depth", "N/A")
        color = get_color_by_depth(depth)
        radius = get_radius_by_magnitude(magnitude)

        tooltip = None
        if magnitude >= 5.0:
            tooltip = f"Mag {magnitude} | {depth} km"

        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=radius,
            color="#111827",
            weight=0.8,
            fill=True,
            fill_color=color,
            fill_opacity=0.76,
            popup=folium.Popup(_popup_html(row), max_width=260),
            tooltip=tooltip,
        ).add_to(detail_group)

    detail_group.add_to(map_obj)

    if len(df) > len(detail_df):
        print(f"⚡ Performans: {len(df)} kaydin tumu hizli cluster ile, en buyuk {len(detail_df)} deprem detayli marker ile gosteriliyor")


def add_heatmap(map_obj, df, name="Yogunluk Haritasi", max_points=MAX_HEAT_POINTS):
    """
    Deprem yogunluk haritasi ekler.
    """
    if df.empty:
        return

    sample_size = min(len(df), max_points)
    df_sample = df.sample(n=sample_size, random_state=42) if len(df) > max_points else df

    heat_data = [
        [row.latitude, row.longitude, getattr(row, "magnitude", 1)]
        for row in df_sample.itertuples(index=False)
    ]

    heat_group = folium.FeatureGroup(name=name, show=False, overlay=True, control=True)
    HeatMap(
        heat_data,
        min_opacity=0.18,
        max_opacity=0.58,
        radius=11,
        blur=14,
        max_zoom=9,
        gradient={0.4: "blue", 0.6: "lime", 0.8: "orange", 1.0: "red"},
    ).add_to(heat_group)

    heat_group.add_to(map_obj)

    if len(df) > max_points:
        print(f"⚡ Heatmap: {len(df)} kayittan {max_points} ornek kullanildi")


def add_fault_lines(map_obj, geojson_path=None):
    """
    Turkiye fay hatlarini haritaya ekler.
    """
    if geojson_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        geojson_path = os.path.join(base_dir, "data", "geo", "turkey_fault_lines.geojson")

    if not os.path.exists(geojson_path):
        print(f"⚠️ Fay hatlari dosyasi bulunamadi: {geojson_path}")
        return

    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            fault_data = json.load(f)

        fault_layer = folium.FeatureGroup(name="Fay Hatlari", show=True, overlay=True, control=True)

        for feature in fault_data["features"]:
            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]

            risk = props.get("risk", "Orta")
            if risk == "Çok Yüksek":
                color = "#8B0000"
                weight = 4
            elif risk == "Yüksek":
                color = "#FF4500"
                weight = 3
            else:
                color = "#FFA500"
                weight = 2

            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 240px; font-size: 12px;">
                <div style="font-weight: 700; margin-bottom: 6px;">{props['name']}</div>
                <div><b>Risk:</b> {risk}</div>
                <div><b>Uzunluk:</b> {props.get('length_km', 'N/A')} km</div>
                <div><b>Tip:</b> {props.get('type', 'N/A')}</div>
                <div style="margin-top: 6px; color: #555;">{props.get('description', '')}</div>
            </div>
            """

            folium.PolyLine(
                locations=[[lat, lon] for lon, lat in coords],
                color=color,
                weight=weight,
                opacity=0.78,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=props["name"],
                smooth_factor=1.2,
            ).add_to(fault_layer)

        fault_layer.add_to(map_obj)
        print(f"✅ {len(fault_data['features'])} fay hatti eklendi")

    except Exception as e:
        print(f"❌ Fay hatlari yukleme hatasi: {e}")


def add_legend(map_obj):
    """
    Haritaya kompakt aciklama kutusu ekler.
    """
    legend_html = """
    <div style="position: fixed;
                bottom: 16px; right: 12px; width: 180px; height: auto;
                background-color: rgba(255, 255, 255, 0.93); z-index:9999; font-size:9px;
                border:1px solid #94a3b8; border-radius: 6px; padding: 6px;
                box-shadow: 0 0 8px rgba(0,0,0,0.24);">
        <h4 style="margin: 0 0 4px 0; text-align: center; color: #333; font-size: 11px;">Harita Aciklama</h4>
        <hr style="margin: 3px 0;">
        <p style="margin: 3px 0 1px 0; font-weight: bold; font-size: 9px;">Buyukluk:</p>
        <p style="margin: 1px 0 1px 12px; line-height: 1.3;"><span style="font-size: 6px;">⬤</span> &lt;4.0 · <span style="font-size: 9px;">⬤</span> 4-5 · <span style="font-size: 12px;">⬤</span> 5-6 · <span style="font-size: 15px;">⬤</span> &gt;6</p>
        <p style="margin: 4px 0 1px 0; font-weight: bold; font-size: 9px;">Derinlik:</p>
        <p style="margin: 1px 0 1px 12px; line-height: 1.4;">
            <span style="color: #FF0000;">⬤</span> &lt;10km ·
            <span style="color: #FF6600;">⬤</span> 10-30 ·
            <span style="color: #FFB300;">⬤</span> 30-70<br>
            <span style="margin-left: 12px;"><span style="color: #FFFF00;">⬤</span> 70-150 ·
            <span style="color: #006400;">⬤</span> &gt;300km</span>
        </p>
        <p style="margin: 4px 0 0 0; color: #475569; font-size: 8px;">Tum kayitlar hizli kumeleme ile, en buyuk depremler detayli popup ile gosterilir.</p>
    </div>
    """
    map_obj.get_root().html.add_child(folium.Element(legend_html))


def create_earthquake_map(df, output_path="map.html"):
    """
    Deprem haritasi olusturur ve kaydeder.
    """
    earthquake_map = create_base_map()

    if not df.empty:
        add_earthquake_markers(earthquake_map, df, use_clustering=True)
        add_heatmap(earthquake_map, df)
        add_fault_lines(earthquake_map)
        add_legend(earthquake_map)

    folium.LayerControl(
        position="topright",
        collapsed=True,
        autoZIndex=True,
    ).add_to(earthquake_map)

    output_path = os.path.abspath(output_path)
    earthquake_map.save(output_path)
    print(f"✅ Harita olusturuldu: {output_path}")

    return output_path


def filter_earthquakes(df, min_magnitude=0.0, max_magnitude=10.0, start_date=None, end_date=None):
    """
    Deprem verilerini filtreler.
    """
    filtered = df.copy()

    filtered = filtered[
        (filtered["magnitude"] >= min_magnitude) & (filtered["magnitude"] <= max_magnitude)
    ]

    if start_date and "time" in filtered.columns:
        filtered = filtered[filtered["time"] >= start_date]
    if end_date and "time" in filtered.columns:
        filtered = filtered[filtered["time"] <= end_date]

    return filtered
