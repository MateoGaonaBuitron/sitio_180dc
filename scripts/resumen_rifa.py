"""Lee el resumen de septiembre y concilia caja y cancelación del préstamo."""
from decimal import Decimal
import openpyxl
import pandas as pd
from helpers import InformeMes


def cargar_septiembre_rifa(path, anterior, deuda_anterior):
    with open(path, 'rb') as source:
        book = openpyxl.load_workbook(source, data_only=True)
    try:
        sheet = book['Hoja 1']
        for celda, texto in {'A4': 'Rifas, segunda parte', 'A5': 'Premios de la rifa',
                             'A6': 'Pago de deuda con Amanda(9/22/26)'}.items():
            if sheet[celda].value != texto:
                raise ValueError(f'Revisar estructura del resumen de la rifa: {celda}')
        def monto(celda):
            v = sheet[celda].value
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ValueError(f'Importe inválido en {celda}')
            d = Decimal(str(v))
            if not d.is_finite():
                raise ValueError(f'Importe no finito en {celda}')
            return d.quantize(Decimal('0.01'))
        inicial, ingresos, premios, pago = monto('D8'), monto('B4'), -monto('B5'), -monto('B6')
        if min(ingresos, premios, pago) < 0:
            raise ValueError('Signos incorrectos en el resumen de la rifa')
        if inicial != Decimal(str(anterior.saldo_final)):
            raise ValueError('La caja inicial de septiembre no coincide con el cierre de agosto')
        prestamo = next(p for p in deuda_anterior['partidas'] if p['fila_excel'] == 27)
        if pago != Decimal(str(prestamo['monto'])):
            raise ValueError('Revisar el pago: no coincide con el préstamo pendiente de Amanda')
        final = inicial + ingresos - premios - pago
        if monto('B7') != ingresos-premios-pago or monto('D9') != ingresos-premios-pago or monto('D10') != final:
            raise ValueError('No cuadran los totales del resumen. Recalcula y guarda el Excel.')
        partidas = [p.copy() for p in deuda_anterior['partidas'] if p['fila_excel'] != 27]
        deuda = sum(Decimal(str(p['monto'])) for p in partidas)
        rows = pd.DataFrame([
            {'Tipo': 'Ingreso', 'Monto': float(ingresos), 'Descripcion': 'Rifas, segunda parte'},
            {'Tipo': 'Egreso', 'Monto': float(premios), 'Descripcion': 'Premios de la rifa'},
            {'Tipo': 'Pago de deuda', 'Monto': float(pago), 'Descripcion': 'Reposición a Amanda Gomez'},
        ])
        info = InformeMes(mes='Septiembre', ciclo='2026-2', responsable='Mateo Gaona',
            actualizacion='02/10/2026', saldo_inicial=float(inicial), ingresos=float(ingresos),
            inversion=0.0, egresos_op=float(premios), pago_deuda=float(pago), saldo_final=float(final),
            df=rows, df_egresos=rows[rows.Tipo=='Egreso'].copy(),
            df_ingresos=rows[rows.Tipo=='Ingreso'].copy(), df_inversion=rows.iloc[:0].copy())
        narrativa = {
            'saldo_despues_de_deuda': True,
            'fuentes_ingresos': [{'nombre': 'Rifas — segunda parte', 'monto': float(ingresos),
                'detalle': str(sheet['G4'].value), 'categoria_ui': 'Recaudación'}],
            'egresos': [
                {'titulo': 'Premios de la rifa', 'monto': float(premios),
                 'para_que': 'Compra de premios de la rifa.', 'categoria_ui': 'Rifas — Premios'},
                {'titulo': 'Pago del préstamo de Amanda Gomez', 'monto': float(pago),
                 'fecha': '22/09/2026', 'para_que': 'Reposición del adelanto para el catering de 180 Talks 2026-1. Préstamo cancelado.',
                 'categoria_ui': 'Pago de deuda', 'pago_deuda': True},
            ],
            'deuda': {'monto': float(deuda), 'seccion_titulo': 'Deudas pendientes', 'partidas': partidas},
            'nota_cierre': 'La segunda parte de la rifa permitió cubrir los premios y cancelar el préstamo de Amanda Gomez el 22 de septiembre. Sigue pendiente la deuda con la Universidad del Pacífico por el catering de 180 Talks 2026-1.',
            'fuente_titulo': 'Resumen de la rifa — Septiembre 2026',
            'fuente_detalle': 'Ingresos de la segunda parte de la rifa, premios, pago del préstamo y cierre de caja.',
        }
        return info, narrativa
    finally:
        book.close()
