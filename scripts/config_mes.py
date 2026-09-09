"""
config_mes.py — Textos del informe de cada mes (los NÚMEROS salen del Excel).

Este archivo SOLO describe en palabras cada ingreso y egreso. Los montos,
saldos y totales se calculan automáticamente desde el archivo Excel del mes
(carpeta data/). Lo que escribas aquí debe coincidir, fila por fila, con ese
Excel.

Por cada INGRESO (lista "fuentes_ingresos"):
  - nombre:   título corto (ej. "Membresías")
  - monto:    monto en soles, sin "S/" (ej. 110.0)
  - detalle:  explicación de una línea
  - fecha:    opcional, "DD/MM/AAAA"

Por cada EGRESO (lista "egresos"):
  - titulo:        nombre legible corto
  - monto:         monto en soles, sin "S/" (ej. 54.83)
  - fecha:         "DD/MM/AAAA" (o rango "DD/MM/AAAA - DD/MM/AAAA")
  - para_que:      ¿en qué se usó el dinero? (frase clara)
  - categoria_ui:  etiqueta para agrupar en el gráfico de torta
  - es_inversion:  True solo si es un bien reutilizable (polos, equipos);
                   en la gran mayoría de casos es False

Y "nota_cierre": un párrafo de resumen del mes. Usa **negritas** con dobles
asteriscos si quieres resaltar algo.

Opcional, "deuda": un préstamo pendiente de reposición (dinero que alguien
adelantó y que la agrupación aún debe). No pasa por la cuenta bancaria, así que
no afecta el saldo; se muestra aparte como pasivo.
  - monto:   monto en soles (ej. 305.50)
  - titulo:  a qué corresponde (ej. "Catering — 180 Talks")
  - detalle: quién adelantó el dinero y en qué condiciones
Si el mes no tiene préstamos pendientes, simplemente no incluyas la clave.
"""

# Marzo 2026-1 ----------------------------------------------------------------
MARZO = {
    "fuentes_ingresos": [
        {
            "nombre": "Membresías (fees mensuales)",
            "monto": 640.0,
            "detalle": "64 aportes de S/10 entre el 23 y 30 de marzo (semana 1 del ciclo).",
            "icono": "👥",
        },
    ],
    "egresos": [
        {
            "titulo": "Catering para la bienvenida",
            "monto": 62.0,
            "fecha": "24/03/2026",
            "para_que": "Snacks y bebidas para la actividad de bienvenida del ciclo (S0).",
            "categoria_ui": "Bienvenida — Insumos",
            "es_inversion": False,
            "icono": "🥨",
        },
        {
            "titulo": "Materiales",
            "monto": 131.17,
            "fecha": "24/03/2026",
            "para_que": "Papelotes, plumones e insumos para dinámicas de la bienvenida.",
            "categoria_ui": "Bienvenida — Insumos",
            "es_inversion": False,
            "icono": "🖍️",
        },
        {
            "titulo": "Photochecks",
            "monto": 50.0,
            "fecha": "13/03/2026",
            "para_que": "Photochecks (credenciales con cordón) para identificar a los miembros.",
            "categoria_ui": "Inversión — Photochecks",
            "es_inversion": True,
            "icono": "🪪",
        },
        {
            "titulo": "Polos institucionales",
            "monto": 120.0,
            "fecha": "13/03/2026 - 18/03/2026",
            "para_que": "Compra de polos con identidad 180DC para miembros del ciclo.",
            "categoria_ui": "Inversión — Polos",
            "es_inversion": True,
            "icono": "👕",
        },
    ],
    "nota_cierre": (
        "Marzo concentra los **gastos de arranque** del ciclo: bienvenida e "
        "inventario institucional (polos y photochecks). El saldo creció porque "
        "los fees del ciclo se cobraron casi en su totalidad durante la primera "
        "semana de clases."
    ),
}

# Abril 2026-1 ----------------------------------------------------------------
ABRIL = {
    "fuentes_ingresos": [
        {
            "nombre": "Membresías (fees mensuales)",
            "monto": 110.0,
            "detalle": "11 aportes entre el 1 y 27 de abril (semanas 2–6 del ciclo).",
            "icono": "👥",
        },
    ],
    "egresos": [
        {
            "titulo": "Capacitación BCG en la UP",
            "monto": 54.83,
            "fecha": "16/04/2026",
            "para_que": "Pago de inscripción/insumos para una capacitación dictada por BCG (Boston Consulting Group) realizada en la Universidad del Pacífico.",
            "categoria_ui": "Capacitación",
            "es_inversion": False,
            "icono": "🎓",
        },
        {
            "titulo": "Reserva local — 1ra Integración",
            "monto": 20.0,
            "fecha": "25/04/2026",
            "para_que": "Reserva de pizzería para la primera actividad de integración del ciclo.",
            "categoria_ui": "Integración",
            "es_inversion": False,
            "icono": "🍕",
        },
        {
            "titulo": "ITF (Impuesto a Transacciones Financieras)",
            "monto": 0.05,
            "fecha": "14/04/2026",
            "para_que": "Impuesto cobrado por el banco al trasladar fondos de Interbank a BCP (consolidación de cuenta operativa).",
            "categoria_ui": "Impuestos / Bancario",
            "es_inversion": False,
            "icono": "🏦",
        },
    ],
    "nota_cierre": (
        "Abril fue un mes de **baja actividad**: caen los fees porque la mayoría "
        "se cobró en marzo, y los egresos se limitaron a una capacitación externa "
        "(BCG en UP), la reserva de la primera integración y el ITF del traslado "
        "bancario Interbank→BCP. No hubo nuevas inversiones."
    ),
}

# Mayo 2026-1 -----------------------------------------------------------------
MAYO = {
    "fuentes_ingresos": [],
    "egresos": [
        {
            "titulo": "Premio rifa de febrero (1ro)",
            "monto": 37.00,
            "fecha": "10/05/2026",
            "para_que": "Entrega de primer premio de la rifa pro fondos realizada en febrero.",
            "categoria_ui": "Rifas — Premios",
            "es_inversion": False,
            "icono": "🎟️",
        },
        {
            "titulo": "Premio rifa de febrero (2do)",
            "monto": 17.00,
            "fecha": "10/05/2026",
            "para_que": "Entrega de segundo premio de la rifa pro fondos realizada en febrero.",
            "categoria_ui": "Rifas — Premios",
            "es_inversion": False,
            "icono": "🎟️",
        },
        {
            "titulo": "Premio rifa de febrero (3ro)",
            "monto": 9.50,
            "fecha": "10/05/2026",
            "para_que": "Entrega de tercer premio de la rifa pro fondos realizada en febrero.",
            "categoria_ui": "Rifas — Premios",
            "es_inversion": False,
            "icono": "🎟️",
        },
        {
            "titulo": "ITF (traspase de cuenta)",
            "monto": 0.05,
            "fecha": "May",
            "para_que": "Impuesto a las transacciones financieras generado por traspase de cuenta.",
            "categoria_ui": "Impuestos / Bancario",
            "es_inversion": False,
            "icono": "🏦",
        },
    ],
    "nota_cierre": (
        "Mayo fue un mes **sin ingresos** y con gasto mínimo: la entrega de "
        "los tres premios pendientes de la rifa pro fondos del mes de febrero "
        "(S/ 37 + S/ 17 + S/ 9.50 = S/ 63.50) más S/ 0.05 de ITF por traspase "
        "bancario. El saldo baja ligeramente pero se mantiene sólido."
    ),
}

# Junio 2026-1 ----------------------------------------------------------------
JUNIO = {
    "fuentes_ingresos": [
        {
            "nombre": "Recaudación — Rifa pro fondos",
            "monto": 100.0,
            "fecha": "15/06/2026 - 30/06/2026",
            "detalle": "Venta de tickets de rifa a S/ 5 cada uno (20 tickets vendidos entre el 15 y 30 de junio). Periodo de venta aún abierto.",
            "categoria_ui": "Recaudación",
            "icono": "🎟️",
        },
        {
            "nombre": "Recaudación — Conexión 180 DC",
            "monto": 15.0,
            "fecha": "29/06/2026 - 30/06/2026",
            "detalle": "Taller abierto Conexión 180 DC a S/ 5 por entrada. 3 participantes inscritos en junio.",
            "categoria_ui": "Recaudación",
            "icono": "🎓",
        },
    ],
    "egresos": [
        {
            "titulo": "Reserva de nombre",
            "monto": 26.40,
            "fecha": "03/06/2026",
            "para_que": "Pago por reserva de nombre ante SUNARP como parte del proceso de constitución de la agrupación.",
            "categoria_ui": "Constitución",
            "es_inversion": False,
            "icono": "📋",
        },
        {
            "titulo": "Costos registrales",
            "monto": 130.00,
            "fecha": "14/06/2026",
            "para_que": "Costos registrales asociados al proceso de constitución formal de la agrupación.",
            "categoria_ui": "Constitución",
            "es_inversion": False,
            "icono": "🏛️",
        },
        {
            "titulo": "Costos notariales",
            "monto": 821.50,
            "fecha": "14/06/2026",
            "para_que": "Honorarios notariales para la escritura pública de constitución de la agrupación.",
            "categoria_ui": "Constitución",
            "es_inversion": False,
            "icono": "⚖️",
        },
        {
            "titulo": "Catering — Pre 180 Talks",
            "monto": 40.00,
            "fecha": "27/06/2026",
            "para_que": "Catering para el evento Pre 180 Talks.",
            "categoria_ui": "Eventos",
            "es_inversion": False,
            "icono": "🥗",
        },
        {
            "titulo": "Regalos para jueces — Pre 180 Talks",
            "monto": 23.60,
            "fecha": "28/06/2026",
            "para_que": "Regalos para los jueces del evento Pre 180 Talks.",
            "categoria_ui": "Eventos",
            "es_inversion": False,
            "icono": "🎁",
        },
        {
            "titulo": "Vasos y bocaditos — Pre 180 Talks",
            "monto": 45.38,
            "fecha": "28/06/2026",
            "para_que": "Vasos y bocaditos para el evento Pre 180 Talks.",
            "categoria_ui": "Eventos",
            "es_inversion": False,
            "icono": "🥤",
        },
        {
            "titulo": "Materiales — Integración (picnic)",
            "monto": 4.40,
            "fecha": "28/06/2026",
            "para_que": "Materiales para la actividad de integración tipo picnic.",
            "categoria_ui": "Integración",
            "es_inversion": False,
            "icono": "🧺",
        },
    ],
    "nota_cierre": (
        "Junio concentra el **gasto más importante del ciclo**: la constitución "
        "formal de 180DC PUCP como persona jurídica (reserva de nombre, costos "
        "registrales y notariales por un total de S/ 977.90). También se "
        "realizaron gastos para el evento Pre 180 Talks (catering, regalos para "
        "jueces y bocaditos por S/ 108.98) y una integración tipo picnic "
        "(S/ 4.40). Por el lado de ingresos, arrancaron dos actividades de "
        "recaudación: la **rifa pro fondos** (S/ 100) y el **taller Conexión "
        "180 DC** (S/ 15), sumando S/ 115 que amortiguan parcialmente los "
        "egresos."
    ),
}

# Julio 2026-1 ----------------------------------------------------------------
JULIO = {
    "fuentes_ingresos": [
        {
            "nombre": "Recaudación — Rifa pro fondos",
            "monto": 135.0,
            "fecha": "01/07/2026 - 17/07/2026",
            "detalle": "Continuación de la venta de tickets de rifa a S/ 5 cada uno. Periodo de venta aún abierto; premios pendientes de entrega.",
            "categoria_ui": "Recaudación",
            "icono": "🎟️",
        },
        {
            "nombre": "Recaudación — Conexión 180 DC",
            "monto": 10.0,
            "fecha": "01/07/2026 - 03/07/2026",
            "detalle": "Taller abierto Conexión 180 DC a S/ 5 por entrada. 2 participantes inscritos en julio (Fernando Zentner, Arianna Malarin).",
            "categoria_ui": "Recaudación",
            "icono": "🎓",
        },
    ],
    "egresos": [
        {
            "titulo": "Reserva de nombre para RUC",
            "monto": 33.00,
            "fecha": "10/07/2026",
            "para_que": "Reserva de nombre necesaria para la obtención del RUC de la agrupación.",
            "categoria_ui": "Constitución / RUC",
            "es_inversion": False,
            "icono": "📋",
        },
        {
            "titulo": "Transporte a notaría",
            "monto": 30.80,
            "fecha": "10/07/2026",
            "para_que": "Transporte a la notaría para tramitar documentos relacionados al RUC.",
            "categoria_ui": "Constitución / RUC",
            "es_inversion": False,
            "icono": "🚕",
        },
        {
            "titulo": "Transporte para trámite RUC",
            "monto": 9.00,
            "fecha": "25/07/2026",
            "para_que": "Transporte para gestiones adicionales de obtención del RUC.",
            "categoria_ui": "Constitución / RUC",
            "es_inversion": False,
            "icono": "🚕",
        },
        {
            "titulo": "Bebidas para Pre 180 Talks",
            "monto": 29.50,
            "fecha": "25/07/2026",
            "para_que": "Reembolso a Mateo por bebidas adquiridas para el evento Pre 180 Talks.",
            "categoria_ui": "Eventos",
            "es_inversion": False,
            "icono": "🥤",
        },
        {
            "titulo": "Bocaditos para integración (picnic)",
            "monto": 23.00,
            "fecha": "25/07/2026",
            "para_que": "Bocaditos y materiales para la actividad de integración tipo picnic.",
            "categoria_ui": "Integración",
            "es_inversion": False,
            "icono": "🧺",
        },
    ],
    "nota_cierre": (
        "Julio cierra con **saldo positivo neto** de S/ 19.70: los ingresos por "
        "rifa y Conexión 180 DC (S/ 145) cubren los egresos operativos "
        "(S/ 125.30), que incluyen trámites de constitución y RUC (S/ 72.80), "
        "bebidas para el Pre 180 Talks (S/ 29.50) y materiales de integración "
        "(S/ 23). El evento principal del mes fue el **180 Talks** (18 de "
        "julio), cuyo catering de S/ 305.50 fue cubierto por un préstamo de "
        "Amanda Gomez, pendiente de reposición sin intereses."
    ),
    "deuda": {
        "monto": 305.50,
        "titulo": "Catering — 180 Talks (18 de julio)",
        "detalle": (
            "Amanda Gomez adelantó S/ 305.50 para cubrir el catering del evento "
            "180 Talks. El pago se realizó directamente al proveedor y no pasó "
            "por la cuenta bancaria de la agrupación. Este monto está "
            "**pendiente de reposición**, sin intereses. Es el único préstamo "
            "vigente."
        ),
    },
}

# Agosto 2026-2 ---------------------------------------------------------------
# Los importes y filas se leen del plan semanal original.
AGOSTO = {
    "actualizacion": "09/09/2026",
    "fuente_titulo": "Plan de Sostenibilidad Financiera 2026-II — Excel original",
    "fuente_detalle": "Descarga el archivo completo. Agosto se obtiene de las semanas S1–S3 de la hoja Flujo de Caja. La deuda heredada se informa aparte de los pagos realizados. Consulta la conciliación semanal.",
    "criterio_semanal": "Se respeta la agrupación del Excel: agosto comprende S1, S2 y S3, incluida la semana del 31/08 que se extiende a septiembre. Las fechas indican el inicio de la semana, no el día exacto de cada operación. El saldo del plan descuenta la deuda heredada; aquí se muestran por separado el disponible y el disponible menos deuda.",
    "nota_cierre": (
        "Agosto parte de **S/ 92.87 disponibles al 17 de agosto**. Los ingresos del stand y las rifas, "
        "menos los gastos de dulces del stand, aumentan el disponible. "
        "La **deuda heredada del ciclo 2026-1 sigue pendiente** y se presenta por separado. "
        "El pago de **S/ 38.62 programado para el 23 de agosto no se ejecutó**, por lo que se retiró del registro de gastos. "
        "El archivo fuente comienza el 17 de agosto; no aporta un detalle de movimientos del 1 al 16."
    ),
    "deuda": {
        "titulo": "Catering — 180 Talks (deuda heredada del 2026-1)",
        "detalle": (
            "Adelanto de Amanda Gomez para el catering del 180 Talks de julio, pendiente de reposición. "
            "El plan lo incorpora en S1 como DEUDA heredada del 2026-I. Su registro no representa "
            "un nuevo desembolso de agosto; se descuenta únicamente al calcular el disponible menos deuda."
        ),
    },
}

# Registro global por mes
NARRATIVA = {
    "Marzo": MARZO,
    "Abril": ABRIL,
    "Mayo": MAYO,
    "Junio": JUNIO,
    "Julio": JULIO,
    "Agosto": AGOSTO,
}
