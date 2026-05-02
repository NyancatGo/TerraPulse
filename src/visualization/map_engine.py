"""
TerraPulse Map Engine
Folium tabanli interaktif harita olusturma modulu.
"""

import json
import os

import folium
import pandas as pd
from folium.map import Layer
from folium.plugins import HeatMap
from jinja2 import Template


MAX_DETAIL_MARKERS = 120
MAX_HEAT_POINTS = 900


class CanvasEarthquakeLayer(Layer):
    """
    Cok sayida deprem noktasini marker objesi uretmeden gercek Leaflet haritasi uzerine cizer.
    """

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = (function() {
                var data = {{ this.data|tojson }};
                var options = {{ this.options|tojson }};

                function depthColor(depth) {
                    if (depth === null || depth === undefined || Number.isNaN(depth)) return "#808080";
                    if (depth < 10) return "#FF0000";
                    if (depth < 30) return "#FF6600";
                    if (depth < 70) return "#FFB300";
                    if (depth < 150) return "#FFFF00";
                    if (depth < 300) return "#90EE90";
                    return "#006400";
                }

                function pointRadius(magnitude, zoom) {
                    var radius = magnitude >= 7 ? 5.8 : magnitude >= 6 ? 5.0 : magnitude >= 5 ? 4.0 : 2.7;
                    if (zoom <= 5) return Math.max(1.6, radius - 0.8);
                    if (zoom >= 8) return radius + 0.8;
                    return radius;
                }

                function escapeHtml(value) {
                    return String(value === null || value === undefined ? "" : value)
                        .replace(/&/g, "&amp;")
                        .replace(/</g, "&lt;")
                        .replace(/>/g, "&gt;")
                        .replace(/"/g, "&quot;")
                        .replace(/'/g, "&#039;");
                }

                function popupHtml(row) {
                    var depth = row[3] === null || row[3] === undefined ? "N/A" : Number(row[3]).toFixed(1);
                    var time = escapeHtml(row[5] || "").slice(0, 19);
                    return [
                        '<div style="font-family: Arial, sans-serif; width: 215px; font-size: 12px;">',
                        '<div style="font-weight: 700; font-size: 14px; margin-bottom: 6px;">Deprem Bilgisi</div>',
                        '<div><b>Buyukluk:</b> ' + escapeHtml(Number(row[2] || 0).toFixed(1)) + '</div>',
                        '<div><b>Konum:</b> ' + escapeHtml(row[4] || "Bilinmiyor") + '</div>',
                        '<div><b>Derinlik:</b> ' + escapeHtml(depth) + ' km</div>',
                        '<div><b>Tarih:</b> ' + time + '</div>',
                        '<div><b>Koordinat:</b> ' + Number(row[0]).toFixed(3) + ', ' + Number(row[1]).toFixed(3) + '</div>',
                        '</div>'
                    ].join('');
                }

                var CanvasLayer = L.Layer.extend({
                    initialize: function(points, layerOptions) {
                        this.points = points || [];
                        L.setOptions(this, layerOptions || {});
                    },
                    onAdd: function(map) {
                        this._map = map;
                        this._canvas = L.DomUtil.create("canvas", "terrapulse-earthquake-canvas leaflet-zoom-animated");
                        this._canvas.style.pointerEvents = "none";
                        this._ctx = this._canvas.getContext("2d", { alpha: true });
                        map.getPane(this.options.pane || "overlayPane").appendChild(this._canvas);

                        map.on("moveend zoomend resize viewreset", this._reset, this);
                        map.on("click", this._handleClick, this);
                        if (map.options.zoomAnimation && L.Browser.any3d) {
                            map.on("zoomanim", this._animateZoom, this);
                        }

                        this._reset();
                    },
                    onRemove: function(map) {
                        map.off("moveend zoomend resize viewreset", this._reset, this);
                        map.off("click", this._handleClick, this);
                        map.off("zoomanim", this._animateZoom, this);
                        L.DomUtil.remove(this._canvas);
                        this._canvas = null;
                        this._ctx = null;
                    },
                    _animateZoom: function(event) {
                        var scale = this._map.getZoomScale(event.zoom);
                        var offset = this._map._latLngBoundsToNewLayerBounds(this._map.getBounds(), event.zoom, event.center).min;
                        L.DomUtil.setTransform(this._canvas, offset, scale);
                    },
                    _reset: function() {
                        if (!this._map || !this._canvas) return;
                        var size = this._map.getSize();
                        var topLeft = this._map.containerPointToLayerPoint([0, 0]);
                        L.DomUtil.setPosition(this._canvas, topLeft);
                        this._canvas.width = size.x;
                        this._canvas.height = size.y;
                        this._draw(topLeft);
                    },
                    _draw: function(topLeft) {
                        var ctx = this._ctx;
                        var map = this._map;
                        if (!ctx || !map) return;

                        var bounds = map.getBounds().pad(0.08);
                        var zoom = map.getZoom();
                        ctx.clearRect(0, 0, this._canvas.width, this._canvas.height);

                        for (var i = 0; i < this.points.length; i++) {
                            var row = this.points[i];
                            var lat = row[0];
                            var lon = row[1];
                            if (!bounds.contains([lat, lon])) continue;

                            var magnitude = row[2] || 0;
                            var depth = row[3];
                            var point = map.latLngToLayerPoint([lat, lon]).subtract(topLeft);
                            var radius = pointRadius(magnitude, zoom);

                            ctx.beginPath();
                            ctx.arc(point.x, point.y, radius, 0, Math.PI * 2, false);
                            ctx.fillStyle = depthColor(depth);
                            ctx.globalAlpha = magnitude >= 5 ? 0.84 : 0.58;
                            ctx.fill();
                            ctx.globalAlpha = 0.72;
                            ctx.strokeStyle = "#0f172a";
                            ctx.lineWidth = 0.7;
                            ctx.stroke();
                        }

                        ctx.globalAlpha = 1;
                    },
                    _nearestPoint: function(layerPoint) {
                        var map = this._map;
                        var bounds = map.getBounds().pad(0.08);
                        var zoom = map.getZoom();
                        var nearest = null;
                        var nearestDistance = Infinity;

                        for (var i = 0; i < this.points.length; i++) {
                            var row = this.points[i];
                            var lat = row[0];
                            var lon = row[1];
                            if (!bounds.contains([lat, lon])) continue;

                            var point = map.latLngToLayerPoint([lat, lon]);
                            var distance = point.distanceTo(layerPoint);
                            var hitRadius = Math.max(8, pointRadius(row[2] || 0, zoom) + 4);

                            if (distance <= hitRadius && distance < nearestDistance) {
                                nearest = row;
                                nearestDistance = distance;
                            }
                        }

                        return nearest;
                    },
                    _handleClick: function(event) {
                        var row = this._nearestPoint(event.layerPoint);
                        if (!row) return;

                        L.popup({ maxWidth: 260 })
                            .setLatLng([row[0], row[1]])
                            .setContent(popupHtml(row))
                            .openOn(this._map);
                    }
                });

                return new CanvasLayer(data, options);
            })();
        {% endmacro %}
        """
    )

    def __init__(self, data, name=None, overlay=True, control=True, show=True):
        super().__init__(name=name, overlay=overlay, control=control, show=show)
        self._name = "CanvasEarthquakeLayer"
        self.data = data
        self.options = {"pane": "overlayPane"}


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


def add_interaction_styles(map_obj):
    """Canvas katmanlarinin pan/zoom mouse olaylarini engellemesini onle."""
    interaction_css = """
    <style>
        .leaflet-overlay-pane canvas {
            pointer-events: none !important;
        }
        .terrapulse-earthquake-canvas {
            pointer-events: none !important;
        }
    </style>
    """
    map_obj.get_root().header.add_child(folium.Element(interaction_css))


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


def _prepare_canvas_points(df: pd.DataFrame) -> list[list[float]]:
    """Canvas katmani icin temiz koordinat verisi hazirla."""
    points = []

    for row in df.itertuples(index=False):
        latitude = getattr(row, "latitude", None)
        longitude = getattr(row, "longitude", None)

        if pd.isna(latitude) or pd.isna(longitude):
            continue

        latitude = float(latitude)
        longitude = float(longitude)
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            continue

        magnitude = getattr(row, "magnitude", 0.0)
        depth = getattr(row, "depth", None)
        place = getattr(row, "place", "Bilinmiyor")
        time_value = getattr(row, "time", "")
        points.append([
            latitude,
            longitude,
            0.0 if pd.isna(magnitude) else float(magnitude),
            None if pd.isna(depth) else float(depth),
            "" if pd.isna(place) else str(place),
            "" if pd.isna(time_value) else str(time_value),
        ])

    return points


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
    canvas_points = _prepare_canvas_points(df)
    CanvasEarthquakeLayer(
        data=canvas_points,
        name="Deprem Noktalari",
        overlay=True,
        control=True,
        show=True,
    ).add_to(map_obj)

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
        print(f"⚡ Performans: {len(canvas_points)} kayit hafif canvas katmaninda, en buyuk {len(detail_df)} deprem detayli popup ile gosteriliyor")


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
        <p style="margin: 4px 0 0 0; color: #475569; font-size: 8px;">Tum kayitlar hafif canvas katmaninda, en buyuk depremler detayli popup ile gosterilir.</p>
    </div>
    """
    map_obj.get_root().html.add_child(folium.Element(legend_html))


def create_earthquake_map(df, output_path="map.html"):
    """
    Deprem haritasi olusturur ve kaydeder.
    """
    earthquake_map = create_base_map()
    add_interaction_styles(earthquake_map)

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
