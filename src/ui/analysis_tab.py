import sys

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QSplitter, QVBoxLayout, QWidget

from ui.components import SurfaceCard

matplotlib.use("QtAgg")


class AnalysisTab(QWidget):
    """
    Matplotlib grafiklerini PyQt6 arayuzu icinde kompakt dark mode yuzeyler olarak sunar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_modern_styling()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(10)

        self.bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.bottom_splitter.setChildrenCollapsible(False)
        self.bottom_splitter.setHandleWidth(10)

        self.fig_time = Figure()
        self.canvas_time = FigureCanvas(self.fig_time)
        self.ax_time = self.fig_time.add_subplot(111)
        self.time_card = self._create_chart_card(self.canvas_time)

        self.fig_hist = Figure()
        self.canvas_hist = FigureCanvas(self.fig_hist)
        self.ax_hist = self.fig_hist.add_subplot(111)
        self.hist_card = self._create_chart_card(self.canvas_hist)

        self.fig_scatter = Figure()
        self.canvas_scatter = FigureCanvas(self.fig_scatter)
        self.ax_scatter = self.fig_scatter.add_subplot(111)
        self.scatter_card = self._create_chart_card(self.canvas_scatter)

        self.bottom_splitter.addWidget(self.hist_card)
        self.bottom_splitter.addWidget(self.scatter_card)

        self.main_splitter.addWidget(self.time_card)
        self.main_splitter.addWidget(self.bottom_splitter)
        self.main_splitter.setSizes([330, 260])
        self.bottom_splitter.setSizes([1, 1])

        main_layout.addWidget(self.main_splitter)

    def _create_chart_card(self, canvas: FigureCanvas):
        canvas.setStyleSheet("background: transparent;")
        card = SurfaceCard(padding=10, spacing=0)
        card.content_layout.addWidget(canvas)
        return card

    def apply_modern_styling(self):
        matplotlib.rc("font", family="Segoe UI", size=9)

        for fig in [self.fig_time, self.fig_hist, self.fig_scatter]:
            fig.patch.set_facecolor("#0d1729")

    def apply_axes_styling(self, ax, title, xlabel, ylabel):
        ax.set_facecolor("#0d1729")
        ax.grid(True, axis="y", linestyle="--", linewidth=0.7, color="#20314c", alpha=0.95)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#243755")
        ax.spines["bottom"].set_color("#243755")

        ax.tick_params(axis="both", colors="#8ea2bd", labelsize=8.5)
        ax.set_title(title, loc="left", pad=10, fontsize=12, fontweight="bold", color="#f8fbff")
        ax.set_xlabel(xlabel, fontsize=9, color="#91a4bc")
        ax.set_ylabel(ylabel, fontsize=9, color="#91a4bc")

    def _draw_empty_state(self, ax, title):
        ax.set_facecolor("#0d1729")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.text(
            0.5,
            0.54,
            "Veri Bulunamadi",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="#b5c7dd",
            transform=ax.transAxes,
        )
        ax.text(
            0.5,
            0.44,
            "Filtre araligini genisleterek tekrar deneyin.",
            ha="center",
            va="center",
            fontsize=9,
            color="#7e93af",
            transform=ax.transAxes,
        )
        ax.set_title(title, loc="left", pad=10, fontsize=12, fontweight="bold", color="#f8fbff")

    def update_charts(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame = None,
        label1: str = "Bölge 1",
        label2: str = "Bölge 2",
    ):
        self.ax_time.clear()
        self.ax_hist.clear()
        self.ax_scatter.clear()

        COLOR1 = "#60a5fa"
        COLOR2 = "#f59e0b"

        if df1 is None:
            df1 = pd.DataFrame()
        if df2 is None:
            df2 = pd.DataFrame()

        def _prepare(df):
            if df.empty:
                return df
            df = df.copy()
            if "time" in df.columns and "date" not in df.columns:
                df = df.rename(columns={"time": "date"})
            if "date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["date"]):
                df["date"] = pd.to_datetime(df["date"])
            return df

        df1 = _prepare(df1)
        df2 = _prepare(df2)

        if df1.empty and df2.empty:
            print("❌ Graph Warning: her iki DataFrame de boş.")
            self._draw_empty_state(self.ax_time, "Zamana Gore Sismik Aktivite")
            self._draw_empty_state(self.ax_hist, "Buyukluk Frekansi")
            self._draw_empty_state(self.ax_scatter, "Derinlik - Buyukluk Iliskisi")
        else:
            try:
                # --- Zaman Serisi ---
                time_drawn = False
                for df, color, label in [(df1, COLOR1, label1), (df2, COLOR2, label2)]:
                    if not df.empty and "date" in df.columns and "magnitude" in df.columns:
                        ds = df.sort_values("date")
                        self.ax_time.scatter(
                            ds["date"], ds["magnitude"],
                            color=color, s=8, alpha=0.60, label=label, linewidths=0,
                        )
                        time_drawn = True
                if time_drawn:
                    self.ax_time.margins(x=0.02)
                    self.apply_axes_styling(self.ax_time, "Zamana Gore Sismik Aktivite", "Tarih", "Buyukluk (Mw)")
                    self.ax_time.legend(frameon=False, labelcolor="#b5c7dd", fontsize=8.5, loc="upper left")
                else:
                    self._draw_empty_state(self.ax_time, "Zamana Gore Sismik Aktivite")

                # --- Büyüklük Histogramı ---
                hist_drawn = False
                for df, color, label in [(df1, COLOR1, label1), (df2, COLOR2, label2)]:
                    if not df.empty and "magnitude" in df.columns:
                        self.ax_hist.hist(
                            df["magnitude"], bins=20, color=color,
                            edgecolor="none", alpha=0.65, label=label,
                        )
                        hist_drawn = True
                if hist_drawn:
                    self.apply_axes_styling(self.ax_hist, "Buyukluk Frekansi", "Buyukluk (Mw)", "Deprem Sayisi")
                    self.ax_hist.legend(frameon=False, labelcolor="#b5c7dd", fontsize=8.5, loc="upper right")
                else:
                    self._draw_empty_state(self.ax_hist, "Buyukluk Frekansi")

                # --- Derinlik–Büyüklük Dağılımı ---
                scatter_drawn = False
                for df, color, label in [(df1, COLOR1, label1), (df2, COLOR2, label2)]:
                    if not df.empty and "magnitude" in df.columns and "depth" in df.columns:
                        self.ax_scatter.scatter(
                            df["magnitude"], df["depth"],
                            color=color, alpha=0.50, s=22, edgecolors="none", label=label,
                        )
                        scatter_drawn = True
                if scatter_drawn:
                    self.ax_scatter.invert_yaxis()
                    self.apply_axes_styling(
                        self.ax_scatter, "Derinlik - Buyukluk Iliskisi", "Buyukluk (Mw)", "Derinlik (km)",
                    )
                    self.ax_scatter.legend(frameon=False, labelcolor="#b5c7dd", fontsize=8.5, loc="lower right")
                else:
                    self._draw_empty_state(self.ax_scatter, "Derinlik - Buyukluk Iliskisi")

            except Exception as e:
                print(f"❌ Matplotlib Çizim Hatası: {e}")
                import traceback
                traceback.print_exc()

        self.fig_time.tight_layout(pad=1.2)
        self.fig_hist.tight_layout(pad=1.2)
        self.fig_scatter.tight_layout(pad=1.2)

        self.canvas_time.draw()
        self.canvas_hist.draw()
        self.canvas_scatter.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    magnitudes = np.random.normal(loc=3.5, scale=1.0, size=100)
    depths = np.random.uniform(5.0, 35.0, size=100)

    dummy_df = pd.DataFrame(
        {
            "date": dates,
            "magnitude": magnitudes,
            "depth": depths,
        }
    )

    window = AnalysisTab()
    window.resize(980, 720)
    window.setWindowTitle("TerraPulse - Karsilastirmali Analiz Testi")
    window.setStyleSheet("background-color: #08111f;")
    dummy_df2 = pd.DataFrame(
        {
            "date": pd.date_range(start="2023-06-01", periods=60, freq="D"),
            "magnitude": np.random.normal(loc=4.0, scale=0.8, size=60),
            "depth": np.random.uniform(10.0, 50.0, size=60),
        }
    )
    window.update_charts(dummy_df, dummy_df2, "Test Bölge 1", "Test Bölge 2")
    window.show()

    sys.exit(app.exec())
