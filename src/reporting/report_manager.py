"""TerraPulse icin otomatik PDF raporlama modulu."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os

try:
    from fpdf import FPDF
except ImportError:  # pragma: no cover - kurulum eksikse kullaniciya yukarida anlatilir
    FPDF = None


def _find_font_paths() -> tuple[str | None, str | None]:
    """Turkce karakterler icin uygun bir regular/bold font bulmaya calis."""
    candidate_pairs = [
        ("C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf"),
        ("C:\\Windows\\Fonts\\segoeui.ttf", "C:\\Windows\\Fonts\\segoeuib.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/Library/Fonts/Arial Unicode.ttf", "/Library/Fonts/Arial Bold.ttf"),
    ]

    for regular_path, bold_path in candidate_pairs:
        if os.path.exists(regular_path):
            return regular_path, bold_path if os.path.exists(bold_path) else None
    return None, None


@dataclass
class ReportSection:
    title: str
    body: str


class TerraPulsePDF(FPDF):
    """Kurumsal baslik ve altbilgi iceren PDF sinifi."""

    def __init__(self, title: str):
        super().__init__()
        self.report_title = title
        self.ui_primary_color = (15, 118, 110)
        self.ui_text_color = (23, 37, 56)
        self.ui_muted_color = (100, 116, 139)
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()

    def header(self):
        self.set_fill_color(10, 22, 40)
        self.rect(0, 0, 210, 22, style="F")
        self.set_text_color(248, 250, 252)
        self.set_font("TerraPulse", "B", 18)
        self.cell(0, 9, "TerraPulse Analiz Raporu", new_x="LMARGIN", new_y="NEXT")
        self.set_font("TerraPulse", "", 9)
        self.set_text_color(203, 213, 225)
        self.cell(0, 5, self.report_title, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_draw_color(203, 213, 225)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_font("TerraPulse", "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, f"Sayfa {self.page_no()}/{{nb}}", align="R")


class ReportManager:
    """Ozet istatistikler, risk sonuclari ve grafiklerden PDF rapor uretir."""

    def __init__(self):
        self.font_regular, self.font_bold = _find_font_paths()

    def generate_report(
        self,
        output_path: str,
        summary_stats: dict,
        risk_results: dict,
        figures: list[tuple[str, object]],
    ) -> str:
        """
        PDF raporu uret ve kaydet.

        Args:
            output_path: Kaydedilecek pdf yolu
            summary_stats: Ozet istatistikler
            risk_results: Risk hesap ozetleri
            figures: [(baslik, matplotlib_figure), ...]
        """
        if FPDF is None:
            raise RuntimeError("PDF raporlama icin 'fpdf2' kutuphanesi kurulu degil.")

        pdf = TerraPulsePDF(title=summary_stats.get("report_scope", "Sismik veri analizi"))
        self._register_fonts(pdf)
        pdf.add_page()

        self._add_intro(pdf, summary_stats)
        self._add_summary_table(pdf, summary_stats)
        self._add_risk_block(pdf, risk_results)
        self._add_executive_note(pdf, summary_stats, risk_results)

        temp_root = os.path.join(os.path.dirname(os.path.abspath(output_path)), ".report_tmp")
        os.makedirs(temp_root, exist_ok=True)
        image_paths = []
        try:
            image_paths = self._export_figures(figures, temp_root)
            self._add_charts(pdf, image_paths)
        finally:
            self._cleanup_exported_images(image_paths)

        output_path = os.path.abspath(output_path)
        pdf.output(output_path)
        return output_path

    def _register_fonts(self, pdf: TerraPulsePDF):
        if self.font_regular:
            pdf.add_font("TerraPulse", "", self.font_regular)
            if self.font_bold:
                pdf.add_font("TerraPulse", "B", self.font_bold)
            else:
                pdf.add_font("TerraPulse", "B", self.font_regular)
        else:
            pdf.set_font("Helvetica", size=11)

    def _add_intro(self, pdf: TerraPulsePDF, summary_stats: dict):
        pdf.set_text_color(*pdf.ui_text_color)
        pdf.set_font("TerraPulse", "B", 14)
        pdf.cell(0, 8, "Rapor Ozeti", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("TerraPulse", "", 10)
        intro = (
            "Bu rapor, TerraPulse uzerinden secilen filtrelere ait deprem kayitlarini, "
            "bolgesel risk hesaplarini ve mevcut analiz grafiklerini tek bir kurumsal cikti "
            "halinde birlestirir."
        )
        pdf.multi_cell(0, 5, intro)
        pdf.ln(3)

        created_at = summary_stats.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.set_text_color(*pdf.ui_muted_color)
        pdf.cell(0, 5, f"Olusturulma Tarihi: {created_at}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    def _add_summary_table(self, pdf: TerraPulsePDF, summary_stats: dict):
        pdf.set_text_color(*pdf.ui_text_color)
        pdf.set_font("TerraPulse", "B", 12)
        pdf.cell(0, 8, "Ozet Istatistikler", new_x="LMARGIN", new_y="NEXT")

        rows = [
            ("Secilen Bolge", summary_stats.get("selected_region", "Tum Turkiye")),
            ("Tarih Araligi", summary_stats.get("date_range", "-")),
            ("Minimum Buyukluk", summary_stats.get("min_magnitude", "-")),
            ("Toplam Deprem Sayisi", str(summary_stats.get("total_earthquakes", "-"))),
            ("En Buyuk Deprem", summary_stats.get("largest_earthquake", "-")),
            ("Ortalama Derinlik", summary_stats.get("average_depth", "-")),
        ]

        self._draw_key_value_rows(pdf, rows)
        pdf.ln(3)

    def _add_risk_block(self, pdf: TerraPulsePDF, risk_results: dict):
        pdf.set_text_color(*pdf.ui_text_color)
        pdf.set_font("TerraPulse", "B", 12)
        pdf.cell(0, 8, "Risk Skorlama Sonuclari", new_x="LMARGIN", new_y="NEXT")

        top_risk = risk_results.get("top_risk", {})
        probability_50y = risk_results.get("probability_50y", "-")

        rows = [
            ("Referans Bolge", top_risk.get("region", "-")),
            ("Yillik Frekans (lambda)", top_risk.get("annual_rate", "-")),
            ("50 Yillik Asilma Olasiligi", probability_50y),
            ("Geri Donus Periyodu", top_risk.get("recurrence_years", "-")),
            ("Risk Seviyesi", top_risk.get("risk_level", "-")),
            ("Risk Skoru", top_risk.get("risk_score", "-")),
        ]

        self._draw_key_value_rows(pdf, rows)

        ranked_rows = risk_results.get("ranked_regions", [])
        if ranked_rows:
            pdf.ln(2)
            pdf.set_font("TerraPulse", "B", 11)
            pdf.cell(0, 7, "Oncelikli Bolgeler", new_x="LMARGIN", new_y="NEXT")
            self._draw_risk_rank_table(pdf, ranked_rows)
        pdf.ln(3)

    def _add_executive_note(self, pdf: TerraPulsePDF, summary_stats: dict, risk_results: dict):
        pdf.set_font("TerraPulse", "B", 12)
        pdf.set_text_color(*pdf.ui_text_color)
        pdf.cell(0, 8, "Yonetsel Degerlendirme", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("TerraPulse", "", 10)

        selected_region = summary_stats.get("selected_region", "Tum Turkiye")
        total_events = summary_stats.get("total_earthquakes", 0)
        top_risk = risk_results.get("top_risk", {})
        note = (
            f"Secilen {selected_region} kapsaminda toplam {total_events} deprem kaydi analiz edilmistir. "
            f"Mevcut risk modeline gore en yuksek oncelik {top_risk.get('region', 'belirlenemeyen bolge')} "
            f"icin {top_risk.get('risk_level', 'belirsiz')} seviyededir. Grafikler, dagilim ve zaman "
            f"egilimlerini birlikte okuyarak karar destek surecini hizlandirmak icin eklenmistir."
        )
        pdf.multi_cell(0, 5, note)
        pdf.ln(2)

    def _draw_key_value_rows(self, pdf: TerraPulsePDF, rows: list[tuple[str, str]]):
        label_w = 58
        value_w = 132
        line_h = 8

        pdf.set_draw_color(226, 232, 240)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font("TerraPulse", "", 10)
        pdf.set_text_color(*pdf.ui_text_color)

        for label, value in rows:
            current_y = pdf.get_y()
            pdf.set_fill_color(241, 245, 249)
            pdf.cell(label_w, line_h, label, border=1, fill=True)
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(value_w, line_h, str(value), border=1, new_x="LMARGIN", new_y="NEXT")
            if pdf.get_y() == current_y:
                pdf.ln(line_h)

    def _draw_risk_rank_table(self, pdf: TerraPulsePDF, ranked_rows: list[dict]):
        headers = [("Bolge", 54), ("Skor", 26), ("Seviye", 34), ("Olasilik", 34), ("Periyot", 38)]
        row_h = 8

        pdf.set_fill_color(15, 118, 110)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("TerraPulse", "B", 9)
        for title, width in headers:
            pdf.cell(width, row_h, title, border=1, fill=True)
        pdf.ln(row_h)

        pdf.set_font("TerraPulse", "", 9)
        for idx, row in enumerate(ranked_rows[:5]):
            pdf.set_text_color(*pdf.ui_text_color)
            fill = idx % 2 == 0
            if fill:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)
            values = [
                row.get("region", "-"),
                row.get("risk_score", "-"),
                row.get("risk_level", "-"),
                row.get("probability", "-"),
                row.get("recurrence_years", "-"),
            ]
            for (_, width), value in zip(headers, values):
                pdf.cell(width, row_h, str(value), border=1, fill=fill)
            pdf.ln(row_h)

    def _export_figures(self, figures: list[tuple[str, object]], tmp_dir: str) -> list[tuple[str, str]]:
        exported = []
        for index, (title, figure) in enumerate(figures, start=1):
            image_path = os.path.join(tmp_dir, f"chart_{index}.png")
            figure.savefig(image_path, dpi=160, bbox_inches="tight", facecolor=figure.get_facecolor())
            exported.append((title, image_path))
        return exported

    def _cleanup_exported_images(self, image_paths: list[tuple[str, str]]):
        for _, image_path in image_paths:
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except OSError:
                pass

    def _add_charts(self, pdf: TerraPulsePDF, image_paths: list[tuple[str, str]]):
        if not image_paths:
            return

        pdf.add_page()
        pdf.set_text_color(*pdf.ui_text_color)
        pdf.set_font("TerraPulse", "B", 13)
        pdf.cell(0, 8, "Grafik Ekleri", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        for title, image_path in image_paths:
            if pdf.get_y() > 210:
                pdf.add_page()

            pdf.set_font("TerraPulse", "B", 11)
            pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
            pdf.image(image_path, x=15, y=pdf.get_y(), w=180)
            pdf.ln(72)
