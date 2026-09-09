# 180DC PUCP — Portal de Transparencia Financiera 

Sitio web que publica, mes a mes, en qué se gasta el dinero de la agrupación.
Está hecho para mantenerse **sin saber programar**: editas un Excel, escribes
unas descripciones, ejecutas un comando y subes los cambios con GitHub Desktop.

🔗 **Sitio publicado:** https://av-gomez.github.io/sitio_180dc/

---

## 1. Cómo funciona (en 30 segundos)

El sitio se arma a partir de **dos fuentes**:

| Fuente               | Qué aporta                               | Dónde está                      |
| -------------------- | ---------------------------------------- | ------------------------------- |
| 📊 **Excel del mes** | Los **números**: saldos, montos, totales | `data/transacciones_<mes>.xlsx` |
| ✍️ **Descripciones** | Los **textos**: en qué se usó cada gasto | `scripts/config_mes.py`         |

Un comando (`python scripts/build.py`) junta ambos y genera las páginas web
dentro de la carpeta `site/`. Al subir los cambios a GitHub, el sitio se
publica solo.

> ⚠️ **Importante:** los números **siempre** salen del Excel. Las descripciones
> que escribes en `config_mes.py` deben coincidir, fila por fila, con ese Excel.
> Así cualquiera puede descargar el Excel y verificar la información.

El portal está organizado por **ciclos académicos**. El ciclo vigente se muestra
primero y los anteriores quedan abajo, en "Histórico": nada de lo publicado se
borra al pasar de ciclo.

---

## 2. Requisitos (instalar una sola vez)

1. **Python** → https://www.python.org/downloads/
   Durante la instalación marca la casilla **"Add Python to PATH"**.

2. **GitHub Desktop** → https://desktop.github.com/
   Inicia sesión y abre (clona) el repositorio `sitio_180dc`.

3. Abre **PowerShell** (o la terminal) en la carpeta del proyecto y ejecuta
   una vez, para instalar las librerías necesarias:
   
   ```powershell
   pip install -r requirements.txt
   ```

---

## 3. Actualizar / corregir un mes que YA existe

### Agosto 2026-2: fuente semanal

Agosto usa `data/180DC_PUCP_Plan_Sostenibilidad_2026-II.xlsx`, que se ofrece
íntegro para descargar. `scripts/plan_sostenibilidad.py` lee S1–S3 de
`Flujo de Caja`, siguiendo la agrupación de `Supuestos` y `Proyecciones`.
La semana del 31/08 se incluye completa; no se conocen fechas individuales.
Los importes del detalle, gráficos y resumen se calculan desde esas celdas.

La deuda heredada de S/ 305.50 sigue pendiente: se separa de los pagos.
El disponible es S/ 119.87 (92.87 + 49 − 22), y el disponible menos deuda
es −S/ 185.63, que coincide con el saldo del plan. El pago programado de
S/ 38.62 del 23/08 no se ejecutó y queda excluido. El antiguo
`data/transacciones_agosto.xlsx` se conserva solo como antecedente sustituido;
no alimenta el portal ni se publica. Septiembre de prueba fue retirado.

Para actualizar este mes, modifica el plan y guárdalo recalculado en Excel,
manteniendo su estructura. El adaptador verifica los totales semanales y
se detiene si no cuadran o cambia el formato. Las otras hojas y semanas
futuras no generan reportes automáticamente. Los textos explicativos de
agosto permanecen en `config_mes.py`.

### Meses con el formato habitual

1. Abre el Excel del mes en `data/` (ej. `data/transacciones_mayo.xlsx`) y
   corrige lo que haga falta. Guarda.

2. Si cambió alguna descripción, edítala en `scripts/config_mes.py`.

3. Regenera el sitio:
   
   ```powershell
   python scripts/build.py
   ```

4. Abre **GitHub Desktop**, escribe un mensaje (ej. "Corrige mayo") y haz
   **Commit to main** → **Push origin**. En 1–2 minutos el sitio se actualiza.

> 🔴 **Regla de oro:** en el commit tienen que ir **los dos lados**: lo que
> cambiaste en `scripts/` y `data/` **y** lo que se regeneró en `site/`. En
> GitHub Desktop, deja marcados **todos** los archivos de la lista antes de
> hacer Commit. Si subes solo `site/`, los scripts quedan desfasados y el
> siguiente `build.py` borra tu trabajo.

---

## 4. Agregar un mes NUEVO

Ejemplo: agregar **Julio**.

### Paso 1 — El Excel del mes

Copia el registro de transacciones de julio a la carpeta `data/` con el nombre
`transacciones_julio.xlsx`.

El Excel debe mantener el **mismo formato** que los meses anteriores (misma hoja
`Transacciones`, misma fila de encabezados con `Ord.`, `Fecha de registro`,
`Monto (S/.)`, `Descripcion`, etc.). Lo más fácil es **duplicar el Excel del mes
anterior** y reemplazar los movimientos.

Reglas del Excel:

- La fila con **`Ord.` = 0** es el **saldo anterior** (el saldo final del mes
  pasado). De ahí arranca el mes.
- Cada movimiento va con su `Ord.` (1, 2, 3…), su fecha en formato
  **DD/MM/AAAA** y su monto.
- Si la descripción contiene la palabra **"ingreso", "fee" o "membresía"**, se
  cuenta como **ingreso**; si no, como **egreso**.

### Paso 2 — Las descripciones

Abre `scripts/config_mes.py` y agrega un bloque para julio copiando el patrón de
un mes existente. Solo usa los campos que se listan al inicio de ese archivo:

```python
JULIO = {
    "fuentes_ingresos": [
        {"nombre": "Membresías", "monto": 80.0,
         "detalle": "8 aportes de S/10 durante julio."},
    ],
    "egresos": [
        {"titulo": "Reserva de local — 2da Integración",
         "monto": 40.0, "fecha": "12/07/2026",
         "para_que": "Reserva del local para la segunda integración del ciclo.",
         "categoria_ui": "Integración",
         "es_inversion": False},
    ],
    "nota_cierre": "En julio la actividad principal fue la 2da integración...",
}
```

Y al final del archivo, agrégalo al registro:

```python
NARRATIVA = {
    "Marzo": MARZO,
    "Abril": ABRIL,
    "Mayo":  MAYO,
    "Junio": JUNIO,
    "Julio": JULIO,   # ← nuevo
}
```

> Si un mes **no tiene ingresos**, deja la lista vacía: `"fuentes_ingresos": []`.
> La sección de ingresos no aparecerá (así el foco queda en lo que se gastó a
> favor de los miembros).

En los ingresos, además de `nombre`, `monto` y `detalle`, puedes agregar
`fecha` (o un rango `"01/07/2026 - 17/07/2026"`) y `categoria_ui`; ambos son
opcionales y se muestran como etiquetas junto al monto.

**Préstamos pendientes (opcional).** Si alguien adelantó dinero de su bolsillo
y la agrupación todavía se lo debe, agrega la clave `deuda` al bloque del mes:

```python
    "deuda": {
        "monto": 305.50,
        "titulo": "Catering — 180 Talks (18 de julio)",
        "detalle": "Amanda Gomez adelantó S/ 305.50 ... **pendiente de reposición**, sin intereses.",
    },
```

Aparece como un indicador extra en la fila de cifras y como una sección
"Préstamo pendiente". **No afecta el saldo**, porque ese dinero nunca pasó por
la cuenta de la agrupación. Si el mes no tiene préstamos, omite la clave.

### Paso 3 — Registrar el mes en la lista

Abre `scripts/build.py` y agrega el mes dentro de **su ciclo**, en la lista
`CICLOS` (está cerca del inicio):

```python
CICLOS = [
    {
        "ciclo": "2026-1",
        "meses": [
            {"mes": "Marzo", "slug": "marzo", "xlsx": "transacciones_marzo.xlsx"},
            ...
            {"mes": "Julio", "slug": "julio", "xlsx": "transacciones_julio.xlsx"},
        ],
    },
    {
        "ciclo": "2026-2",
        "meses": [
            {"mes": "Agosto",    "slug": "agosto",    "xlsx": "transacciones_agosto.xlsx"},
            {"mes": "Setiembre", "slug": "setiembre", "xlsx": "transacciones_setiembre.xlsx"},  # ← nuevo
        ],
    },
]
```

- `mes`: nombre con mayúscula (debe coincidir con la clave en `config_mes.py`).
- `slug`: el nombre del archivo web, en minúsculas y sin tildes. **Tiene que ser
  único en todo el portal**: si un mes se repite en un ciclo posterior (otro
  Marzo, por ejemplo), usa `"marzo-2027-1"`. Si se repite, `build.py` se detiene
  y te dice qué cambiar.
- `xlsx`: el nombre exacto del Excel en `data/`.

> Si registras un mes cuyo Excel todavía no está en `data/`, `build.py` **no
> falla**: genera el resto del sitio y avisa
> `AVISO: Agosto (2026-2) esta registrado pero falta data/transacciones_agosto.xlsx`.
> El mes aparece en el portal recién cuando pongas el archivo.

### Paso 4 — Generar y subir

```powershell
python scripts/build.py
```

Revisa el **cuadre** que imprime al final (ver sección 7), y sube con
GitHub Desktop (Commit → Push).

---

## 5. Empezar un CICLO nuevo (ej. 2026-2)

El portal guarda **todos los ciclos**: el vigente arriba y los anteriores abajo,
en la sección "Histórico". Un ciclo nuevo se **agrega**, nunca se reemplaza —
así no se borra la información ya publicada.

1. En `scripts/build.py`, agrega un bloque al final de `CICLOS`:
   
   ```python
   {
       "ciclo": "2026-2",
       "meses": [
           {"mes": "Agosto", "slug": "agosto", "xlsx": "transacciones_agosto.xlsx"},
       ],
   },
   ```
2. Apunta el ciclo vigente al nuevo:
   
   ```python
   CICLO_ACTIVO = "2026-2"
   ```
3. En `scripts/config_mes.py`, agrega los bloques de los meses nuevos (no borres
   los anteriores) y regístralos en `NARRATIVA`.
4. En `data/`, agrega los nuevos Excel. El primer mes del ciclo debe traer en su
   fila `Ord. = 0` el **saldo con el que arranca** el ciclo, que es el saldo
   final del último mes del ciclo anterior.

> Cada página muestra el ciclo al que pertenece en la cabecera y el pie, y su
> menú lista solo los meses de ese ciclo. Desde "Inicio" se llega a todos.

> 🧹 `build.py` **borra solo** las páginas y descargas que ya no correspondan a
> ningún mes de `CICLOS`. Si quitas un mes de la lista, su página desaparece del
> sitio (te avisa con una línea `LIMPIEZA ->`).

---

## 6. Reglas contables aplicadas

- **Ingresos:** lo que entra a caja en el mes (membresías, donaciones,
  recaudaciones de eventos, patrocinios).
- **Egresos operativos:** consumibles del mes (bocaditos, transporte, ITF,
  capacitaciones, integraciones, premios de rifa, trámites).
- **Inversión IME** (Inventario / Material reutilizable): bienes que se quedan
  con la agrupación y se reutilizan en ciclos futuros (polos, photochecks,
  equipamiento). Se descuentan del saldo, pero se muestran **separados** para
  que un mes con compra de inventario no parezca deficitario.
- **Saldo final** = Saldo inicial + Ingresos − Egresos operativos − Inversión.
- **Préstamo pendiente (pasivo):** dinero que un miembro adelantó y que la
  agrupación aún debe. Como no salió de la cuenta, **no entra en el saldo**; se
  informa aparte para que la deuda quede visible.

En la práctica, casi todos los gastos son **operativos** (`es_inversion: False`).
Usa `es_inversion: True` solo para bienes reutilizables.

---

## 7. Verificación (el "cuadre")

Cada vez que ejecutas `python scripts/build.py`, imprime un resumen:

```
=== Cuadre ===
-- Ciclo 2026-1
Marzo     Ingresos: S/ 640.00  Egresos op.: S/ 193.17  Inv: S/ 290.00  Saldo final: S/ 1,077.88
Abril     Ingresos: S/ 110.00  Egresos op.: S/  74.88  Inv: S/   0.00  Saldo final: S/ 1,113.00
```

El **saldo final** de cada mes debe ser igual al **saldo inicial del mes
siguiente** (la fila `Ord. = 0` del Excel siguiente). Si no coincide, revisa los
montos del Excel. Entre ciclos vale lo mismo: el último saldo del ciclo que
termina es el saldo de arranque del ciclo que empieza (julio 2026-1 cerró en
S/ 92.87 y agosto 2026-2 arranca con esa misma cifra).

Además del cuadre, `build.py` puede imprimir dos tipos de mensaje:

- `AVISO: <Mes> (<ciclo>) esta registrado pero falta data/<archivo>.xlsx` →
  registraste el mes pero todavía no pusiste su Excel. El resto del sitio se
  genera igual.
- `LIMPIEZA -> se elimino site/meses/<mes>.html` → esa página ya no corresponde
  a ningún mes de `CICLOS` y se borró del sitio.

Para ver el sitio en tu computadora antes de subirlo:

```powershell
python -m http.server 8000 --directory site
```

Luego abre http://localhost:8000 en el navegador.

---

## 8. Estructura de carpetas

```
sitio_180dc/
├── data/                      Excel fuente de cada mes (los NÚMEROS)
│   └── transacciones_<mes>.xlsx
├── scripts/
│   ├── build.py               Genera el sitio. Aquí están CICLOS y CICLO_ACTIVO
│   ├── config_mes.py          Las descripciones de cada mes (los TEXTOS)
│   └── helpers.py             Lee y procesa el Excel (no necesitas tocarlo)
├── site/                      Sitio web generado (se sube tal cual a GitHub Pages)
│   ├── index.html
│   ├── meses/<mes>.html
│   ├── downloads/             Copia de los Excel para descargar
│   └── assets/                Estilos (style.css) y logo (180.jpg)
├── requirements.txt           Librerías de Python
└── README.md                  Este archivo
```

> **No edites a mano** los archivos dentro de `site/`: se sobrescriben cada vez
> que corres `build.py`. Edita siempre el Excel (`data/`) y `config_mes.py`.

---

## 9. Problemas comunes

- **"python no se reconoce…"** → Python no quedó en el PATH. Reinstálalo
  marcando "Add Python to PATH".
- **"No module named pandas/openpyxl"** → ejecuta `pip install -r requirements.txt`.
- **Cambié algo pero el sitio no se actualiza** → ¿ejecutaste `python
  scripts/build.py` **antes** de hacer Commit/Push? El sitio publica lo que hay
  en `site/`, y esa carpeta solo cambia cuando corres el comando.
- **El total no coincide con la suma de las filas** → algún monto en
  `config_mes.py` no coincide con el del Excel. Recuerda: los totales salen del
  Excel; tus descripciones deben reflejar esas mismas filas.
- **Agregué un mes pero no aparece en el sitio** → mira la última línea que
  imprime `build.py`. Si dice `AVISO: ... falta data/transacciones_<mes>.xlsx`,
  el Excel no está en `data/` o tiene otro nombre.
- **`ERROR: el slug "..." se repite`** → dos meses de ciclos distintos quieren el
  mismo archivo web. Ponle al más nuevo un slug con el ciclo, ej. `marzo-2027-1`.
- **Se me borró una página del sitio** → si sacaste ese mes de `CICLOS`,
  `build.py` la elimina a propósito. Vuelve a registrarlo y regenera.
