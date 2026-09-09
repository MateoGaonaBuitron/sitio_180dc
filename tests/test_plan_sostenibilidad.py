"""Verifica el cierre corregido, su trazabilidad y la publicación local."""
from pathlib import Path
import hashlib
from html.parser import HTMLParser
import sys
import unittest
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from config_mes import AGOSTO
from plan_sostenibilidad import cargar_agosto_plan
from build import svg_donut, fmt_fecha_corta

SOURCE = ROOT / "data/180DC_PUCP_Plan_Sostenibilidad_2026-II.xlsx"


class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.info, cls.narrativa = cargar_agosto_plan(SOURCE, AGOSTO)

    def test_caja_excluye_deuda_y_pago_no_ejecutado(self):
        self.assertEqual(self.info.saldo_inicial, 92.87)
        self.assertEqual(self.info.ingresos, 49)
        self.assertEqual(self.info.egresos_op, 22)
        self.assertEqual(self.info.saldo_final, 119.87)
        self.assertEqual(self.narrativa["deuda"]["monto"], 305.5)
        self.assertEqual(len(self.info.df), 4)
        self.assertNotIn(38.62, self.info.df["Monto"].tolist())
        self.assertNotIn(305.5, self.info.df["Monto"].tolist())

    def test_conciliacion_y_detalle_semanal(self):
        semanas = self.narrativa["semanas"]
        self.assertEqual([s["neto"] for s in semanas], [-212.63, -190.63, -185.63])
        self.assertEqual([s["disponible"] for s in semanas], [92.87, 114.87, 119.87])
        self.assertEqual(sum(x["monto"] for x in self.narrativa["fuentes_ingresos"]), self.info.ingresos)
        self.assertEqual(sum(x["monto"] for x in self.narrativa["egresos"]), self.info.egresos_op)
        self.assertEqual(fmt_fecha_corta("Semana del 31/08/2026"), "Semana del 31/08/2026")

    def test_descarga_original_y_prueba_retirada(self):
        download = ROOT / "site/downloads" / SOURCE.name
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).digest(), hashlib.sha256(download.read_bytes()).digest())
        self.assertFalse((ROOT / "site/meses/septiembre-prueba.html").exists())
        self.assertFalse((ROOT / "site/downloads/transacciones_agosto.xlsx").exists())
        html = (ROOT / "site/meses/agosto.html").read_text(encoding="utf-8")
        self.assertIn("S/ 119.87", html)
        self.assertIn("S/ -185.63", html)
        self.assertIn("no se ejecutó", html)
        self.assertIn(SOURCE.name, html)

    def test_enlaces_locales(self):
        class Links(HTMLParser):
            def handle_starttag(self, tag, attrs):
                for key, value in attrs:
                    if key in ("href", "src") and value:
                        self.links.append(value)
        for page in (ROOT / "site").rglob("*.html"):
            parser = Links()
            parser.links = []
            parser.feed(page.read_text(encoding="utf-8"))
            for link in parser.links:
                url = urlparse(link)
                if not url.scheme and not url.netloc and url.path:
                    self.assertTrue((page.parent / unquote(url.path)).exists(), f"Enlace roto: {page.name}: {link}")
            self.assertNotIn("septiembre-prueba", page.read_text(encoding="utf-8"))

    def test_grafico_categoria_unica(self):
        svg = svg_donut(["Stand"], [22], ["#7AB929"], "S/ 22.00")
        self.assertIn("<circle", svg)
        self.assertIn('stroke="#7AB929"', svg)


if __name__ == "__main__":
    unittest.main()
