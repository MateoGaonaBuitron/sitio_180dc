"""
helpers.py — Carga, limpia y clasifica el Registro de Transacciones mensual.
Una sola fuente de verdad para el informe (Quarto y/o script directo).
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import re

# Reglas para sub-categorizar la descripción (mapeo -> categoría legible para gráficos).
# Orden importa: la primera regla que matchea gana.
REGLAS_CATEGORIA = [
    (r"polos|photocheck", "Polos / Photochecks"),
    (r"bocadito|insumo|material|papelote", "Bienvenida — Insumos"),
    (r"capacitaci", "Capacitación"),
    (r"itf|impuesto", "ITF / Impuestos"),
    (r"pizza|integraci", "Integración"),
    (r"reserva de nombre|registral|notarial|constituci", "Constitución"),
    (r"ruc", "RUC"),
    (r"180 talks|talks", "180 Talks"),
    (r"rifa", "Rifas"),
    (r"curso", "Cursos"),
    (r"fee|membres", "Membresías"),
    (r"donaci", "Donaciones"),
    (r"patrocin", "Patrocinios"),
]

@dataclass
class InformeMes:
    mes: str                       # "Marzo" / "Abril"
    ciclo: str                     # "2026-1"
    responsable: str
    actualizacion: str
    saldo_inicial: float
    ingresos: float
    inversion: float               # IME / inventario
    egresos_op: float              # egresos operativos
    saldo_final: float
    df: pd.DataFrame               # transacciones limpias
    df_egresos: pd.DataFrame       # solo egresos operativos
    df_inversion: pd.DataFrame
    df_ingresos: pd.DataFrame
    pago_deuda: float = 0.0         # Reposición de préstamos, separada del gasto operativo


def _excel_serial_to_date(v):
    """Convierte fechas en formato seriado de Excel (e.g. 46026) a datetime."""
    if pd.isna(v):
        return pd.NaT
    if isinstance(v, (int, float)):
        # serial de Excel (días desde 1899-12-30)
        try:
            return pd.Timestamp("1899-12-30") + timedelta(days=float(v))
        except Exception:
            return pd.NaT
    if isinstance(v, str):
        # intenta parsear "13/03/2026"
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return pd.Timestamp(datetime.strptime(v.strip(), fmt))
            except Exception:
                pass
        try:
            return pd.Timestamp(v)
        except Exception:
            return pd.NaT
    return pd.Timestamp(v)


def _clasificar(descripcion: str, rubro: str) -> str:
    txt = f"{rubro or ''} {descripcion or ''}".lower()
    for patt, cat in REGLAS_CATEGORIA:
        if re.search(patt, txt):
            return cat
    return "Otros"


def cargar_mes(xlsx_path: str, mes: str, ciclo: str = "2026-1") -> InformeMes:
    """Lee el archivo de transacciones del mes y devuelve un InformeMes consolidado."""
    MESES = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
             "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12}
    mes_num = MESES.get(mes.strip().lower())
    anio = int(ciclo.split("-")[0]) if "-" in ciclo else 2026

    # Hoja Transacciones (la principal) — encabezado real está en fila 8 (0-indexada 7)
    raw = pd.read_excel(xlsx_path, sheet_name="Transacciones", header=None)
    # Detectar fila de encabezado buscando "Ord."
    hdr_row = None
    for i in range(min(20, len(raw))):
        if any(str(c).strip() == "Ord." for c in raw.iloc[i].values):
            hdr_row = i
            break
    if hdr_row is None:
        raise ValueError("No se encontró fila de encabezado 'Ord.' en Transacciones")
    df = pd.read_excel(xlsx_path, sheet_name="Transacciones", header=hdr_row)
    df.columns = [str(c).strip() for c in df.columns]

    # Mantener filas con Ord. >= 0 numérico
    df = df[pd.to_numeric(df["Ord."], errors="coerce").notna()].copy()
    df["Ord."] = df["Ord."].astype(float).astype(int)

    # Renombrar
    rename = {
        "Fecha de registro": "Fecha",
        "Nombre de la Actividad": "Rubro",
        "Monto (S/.)": "Monto",
        "Descripcion": "Descripcion",
        "Glosa": "Glosa",
    }
    df = df.rename(columns=rename)
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0.0)
    df["Fecha"] = df["Fecha"].apply(_excel_serial_to_date)

    # Corrección: si una fecha parseada cae fuera del mes target, probar swap día/mes.
    # Esto cubre el caso en que Excel guardó la fecha como serial interpretado MM/DD/AAAA
    # cuando en realidad era DD/MM/AAAA (formato latino).
    if mes_num is not None:
        def _corregir(fecha):
            if pd.isna(fecha):
                return fecha
            if fecha.year == anio and fecha.month == mes_num:
                return fecha
            # intento de swap día <-> mes
            try:
                swap = pd.Timestamp(year=fecha.year, month=fecha.day, day=fecha.month)
                if swap.year == anio and swap.month == mes_num:
                    return swap
            except (ValueError, OverflowError):
                pass
            return fecha
        df["Fecha"] = df["Fecha"].apply(_corregir)

    # Responsable / actualización
    meta = pd.read_excel(xlsx_path, sheet_name="Transacciones", header=None, nrows=6)
    resp = "Lesly Guzmán"
    actu = ""
    try:
        # busca "Responsable" en la primera columnita
        for i in range(len(meta)):
            row = [str(x) for x in meta.iloc[i].values]
            if any("Responsable" in s for s in row):
                # la fila siguiente normalmente trae nombre y fecha
                nxt = meta.iloc[i+1].values
                cells = [str(x).strip() for x in nxt if str(x) != "nan"]
                if cells:
                    resp = cells[0]
                    if len(cells) > 1:
                        actu = cells[-1]
                break
    except Exception:
        pass

    # Saldo inicial (fila Ord. == 0)
    fila_saldo = df[df["Ord."] == 0]
    saldo_inicial = float(fila_saldo["Monto"].iloc[0]) if len(fila_saldo) else 0.0

    # Movimientos reales (Ord. > 0)
    mov = df[df["Ord."] > 0].copy()

    # Tipo de flujo: a partir de la descripción / glosa
    def _tipo(row):
        d = (str(row.get("Descripcion","")) + " " + str(row.get("Glosa",""))).lower()
        if "ingreso" in d or "fee" in d or "membres" in d:
            return "Ingreso"
        return "Egreso"
    mov["Tipo"] = mov.apply(_tipo, axis=1)

    # Sub-clasificación
    mov["Categoria"] = mov.apply(lambda r: _clasificar(r.get("Descripcion",""), r.get("Rubro","")), axis=1)

    # Inversión vs egreso operativo
    # Regla: es inversión si la categoría es 'Polos / Photochecks' (inventario reutilizable).
    # Los bocaditos/materiales son consumibles -> egreso operativo, aunque vengan bajo el
    # rubro 'Inventarios de equipo' en el archivo fuente.
    CATEGORIAS_INVERSION = {"Polos / Photochecks"}
    mov["EsInversion"] = mov.apply(
        lambda r: r["Tipo"] == "Egreso" and r["Categoria"] in CATEGORIAS_INVERSION,
        axis=1,
    )

    ingresos = float(mov.loc[mov["Tipo"] == "Ingreso", "Monto"].sum())
    inversion = float(mov.loc[mov["EsInversion"], "Monto"].sum())
    egresos_op = float(mov.loc[(mov["Tipo"] == "Egreso") & (~mov["EsInversion"]), "Monto"].sum())
    saldo_final = saldo_inicial + ingresos - inversion - egresos_op

    df_egresos = mov[(mov["Tipo"] == "Egreso") & (~mov["EsInversion"])].copy()
    df_inversion = mov[mov["EsInversion"]].copy()
    df_ingresos = mov[mov["Tipo"] == "Ingreso"].copy()

    return InformeMes(
        mes=mes,
        ciclo=ciclo,
        responsable=resp,
        actualizacion=actu,
        saldo_inicial=saldo_inicial,
        ingresos=ingresos,
        inversion=inversion,
        egresos_op=egresos_op,
        saldo_final=saldo_final,
        df=mov,
        df_egresos=df_egresos,
        df_inversion=df_inversion,
        df_ingresos=df_ingresos,
    )


def fmt_soles(x: float) -> str:
    return f"S/ {x:,.2f}"
