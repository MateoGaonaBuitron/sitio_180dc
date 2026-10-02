from pathlib import Path
import sys
import unittest
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from config_mes import AGOSTO
from plan_sostenibilidad import cargar_agosto_plan
from resumen_rifa import cargar_septiembre_rifa


class RifaTests(unittest.TestCase):
    def test_concilia_caja_y_cancela_solo_prestamo_amanda(self):
        agosto, narrativa = cargar_agosto_plan(ROOT/'data/180DC_PUCP_Plan_Sostenibilidad_2026-II.xlsx', AGOSTO)
        info, contenido = cargar_septiembre_rifa(ROOT/'data/resumen_rifa_septiembre.xlsx', agosto, narrativa['deuda'])
        self.assertEqual((info.saldo_inicial, info.ingresos, info.egresos_op, info.pago_deuda, info.saldo_final),
                         (119.87, 575, 130, 305.5, 259.37))
        self.assertEqual(contenido['deuda']['monto'], 38.62)
        self.assertEqual(len(contenido['deuda']['partidas']), 1)
        self.assertIn('UP', contenido['deuda']['partidas'][0]['titulo'])
        self.assertEqual(round(info.saldo_final-contenido['deuda']['monto'], 2), 220.75)
        self.assertEqual(sum(e['monto'] for e in contenido['egresos']), 435.5)

    def test_publicacion_y_descarga(self):
        page = (ROOT/'site/meses/septiembre.html').read_text(encoding='utf-8')
        for text in ['S/ 220.75', 'S/ 259.37', 'S/ 305.50', 'S/ 38.62', '22 Set', 'Préstamo cancelado.', 'Mateo Gaona']:
            self.assertIn(text, page)
        a = (ROOT/'data/resumen_rifa_septiembre.xlsx').read_bytes()
        b = (ROOT/'site/downloads/resumen_rifa_septiembre.xlsx').read_bytes()
        self.assertEqual(hashlib.sha256(a).digest(), hashlib.sha256(b).digest())
        index = (ROOT/'site/index.html').read_text(encoding='utf-8')
        self.assertIn('meses/septiembre.html', index)
        self.assertIn('Pagos de deuda', index)


if __name__ == '__main__':
    unittest.main()
