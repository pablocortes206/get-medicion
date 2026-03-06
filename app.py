from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, Dict

import pandas as pd
import streamlit as st


# ==============================
# ESTILO TECK (HEADER)
# ==============================

TECK_GREEN = "#007A3D"   # si tienes el HEX exacto, lo cambiamos
TECK_GREEN_2 = "#00A04A"
TECK_DARK = "#0B0F14"


def inject_teck_style():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(1200px 800px at 10% 10%, #101826 0%, {TECK_DARK} 55%, #070A0E 100%);
        }}

        .block-container {{
            padding-top: 1.0rem !important;
            padding-bottom: 2.0rem !important;
        }}

        .teck-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 16px 20px;
            border-radius: 16px;
            background: linear-gradient(90deg, rgba(0,122,61,.28) 0%, rgba(0,160,74,.12) 45%, rgba(255,255,255,.03) 100%);
            border: 1px solid rgba(0,160,74,.35);
            box-shadow: 0 12px 30px rgba(0,0,0,.35);
            margin-bottom: 18px;
        }}

        .teck-badge {{
            padding: 8px 12px;
            border-radius: 999px;
            font-size: .85rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(180deg, {TECK_GREEN_2} 0%, {TECK_GREEN} 100%);
            border: 1px solid rgba(255,255,255,.18);
            white-space: nowrap;
        }}

        div.stButton > button {{
            border-radius: 12px !important;
            font-weight: 800 !important;
            border: 1px solid rgba(0,160,74,.35) !important;
        }}
        div.stButton > button[kind="primary"] {{
            background: linear-gradient(180deg, {TECK_GREEN_2} 0%, {TECK_GREEN} 100%) !important;
        }}

        [data-testid="stDataFrame"] {{
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,.08);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    st.markdown(
        f"""
        <div class="teck-header">
          <div>
            <p style="font-size:56px; font-weight:900; margin:0; line-height:1.05;">
              GET Wear Monitor
            </p>
            <p style="font-size:24px; margin:6px 0 0 0; opacity:.92;">
              Sistema de monitoreo y proyección de desgaste de cuchillas
            </p>
            <p style="font-size:16px; margin:10px 0 0 0; opacity:.82;">
              <b>Creado por:</b> Pablo Cortés Ramos · Ingeniero de Mantenimiento / Confiabilidad
            </p>
          </div>
          <div class="teck-badge">Teck QB2 · GET Wear Monitor</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================
# CONFIG
# ==============================

DB_PATH = "mediciones.db"

EQUIPOS = [
    "101", "102", "103", "104", "105", "106", "108",
    "201", "202", "203", "204", "205",  # 205 agregado
    "301", "302", "303",
]

EQUIPOS_MOTONIVELADORA = {"301", "302", "303"}

# Reglas: % = DESGASTE (100% malo / 0% bueno)
REGLAS: Dict[str, dict] = {
    "MOTONIVELADORA": {
        "puntos": [
            (122, 100),
            (145, 91),
            (167, 78),
            (190, 65),
            (212, 52),
            (235, 39),
            (257, 26),
            (280, 13),
            (302, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 90, "Cambiar cuchilla / condición inaceptable (rojo)."),
            ("MEDIO", 65, "Monitorear condición (amarillo)."),
            ("OK", 0, "Operación normal (verde)."),
        ],
        "mm_critico": 145.0,
        "label_pct": "Desgaste (%)",
    },
    "DOZER_854_D10_D11": {
        "puntos": [
            (110, 100),
            (120, 83),
            (130, 67),
            (140, 50),
            (150, 33),
            (160, 17),
            (170, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 83, "Cambiar cuchilla inmediatamente (rojo)."),
            ("MEDIO", 50, "Programar / monitorear (amarillo)."),
            ("OK", 0, "Operación normal (verde)."),
        ],
        "mm_critico": 120.0,
        "label_pct": "Desgaste (%)",
    },
}

HORAS_POR_DIA = 24
N_TASA = 5  # promedio últimas N mediciones por equipo


# ==============================
# MODELO
# ==============================

@dataclass
class Resultado:
    mm_izq: float
    mm_der: float
    mm_usada: float
    desgaste_pct: float
    estado: str
    accion: str
    horometro: float
    tasa_mm_h: Optional[float]
    horas_a_critico: Optional[float]
    dias_a_critico: Optional[float]
    regla: str


# ==============================
# DB (init + helpers)
# ==============================

def init_db():
    """
    Crea una tabla base compatible con tu app.
    Si tu DB ya existe con más/otras columnas, NO la rompe.
    """
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            equipo TEXT NOT NULL,
            ubicacion TEXT,
            usuario TEXT,

            horometro REAL,
            mm_izq REAL,
            mm_der REAL,
            mm_usada REAL,

            condicion_pct REAL,
            estado TEXT,
            accion TEXT,

            tasa_mm_h REAL,
            horas_a_critico REAL,
            dias_a_critico REAL
        )
        """)
        con.commit()


def migrar_db_agregar_columnas():
    """
    Agrega columnas nuevas si faltan (no borra datos).
    """
    with sqlite3.connect(DB_PATH) as con:
        cols = {row[1] for row in con.execute("PRAGMA table_info(mediciones)").fetchall()}

        def add(sql_col: str):
            con.execute(f"ALTER TABLE mediciones ADD COLUMN {sql_col}")

        if "fecha" not in cols: add("fecha TEXT")
        if "equipo" not in cols: add("equipo TEXT")
        if "ubicacion" not in cols: add("ubicacion TEXT")
        if "usuario" not in cols: add("usuario TEXT")

        if "horometro" not in cols: add("horometro REAL")
        if "mm_izq" not in cols: add("mm_izq REAL")
        if "mm_der" not in cols: add("mm_der REAL")
        if "mm_usada" not in cols: add("mm_usada REAL")

        if "condicion_pct" not in cols: add("condicion_pct REAL")
        if "estado" not in cols: add("estado TEXT")
        if "accion" not in cols: add("accion TEXT")

        if "tasa_mm_h" not in cols: add("tasa_mm_h REAL")
        if "horas_a_critico" not in cols: add("horas_a_critico REAL")
        if "dias_a_critico" not in cols: add("dias_a_critico REAL")

        con.commit()


def tabla_info(tabla: str) -> list[dict]:
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(f"PRAGMA table_info({tabla})").fetchall()
    return [
        {"name": r[1], "type": (r[2] or "").upper(), "notnull": bool(r[3]), "dflt": r[4]}
        for r in rows
    ]


def valor_default_por_tipo(sql_type: str):
    t = (sql_type or "").upper()
    if "INT" in t:
        return 0
    if "REAL" in t or "FLOA" in t or "DOUB" in t or "NUM" in t or "DEC" in t:
        return 0.0
    return ""


def guardar_medicion(
    equipo: str,
    ubicacion: Optional[str],
    usuario: Optional[str],
    horometro: float,
    mm_izq: float,
    mm_der: float,
    mm_usada: float,
    desgaste_pct: float,
    estado: str,
    accion: str,
    tasa_mm_h: Optional[float],
    horas_a_critico: Optional[float],
    dias_a_critico: Optional[float],
):
    """
    INSERT adaptativo al esquema REAL de tu DB.
    - Si existe 'mm' NOT NULL, se llena con mm_usada.
    - Si existe 'componente' NOT NULL, se llena con 'Cuchilla'.
    - Si aparecen otras NOT NULL legacy, se les da default seguro.
    """
    info = tabla_info("mediciones")

    now = datetime.now().isoformat(timespec="seconds")
    base = {
        "fecha": now,
        "equipo": equipo,
        "ubicacion": (ubicacion or "").strip() or None,
        "usuario": (usuario or "").strip() or None,

        "horometro": float(horometro),
        "mm_izq": float(mm_izq),
        "mm_der": float(mm_der),
        "mm_usada": float(mm_usada),

        # aunque sea desgaste, tu BD lo guarda como condicion_pct
        "condicion_pct": float(desgaste_pct),
        "estado": estado,
        "accion": accion,

        "tasa_mm_h": float(tasa_mm_h) if tasa_mm_h is not None else None,
        "horas_a_critico": float(horas_a_critico) if horas_a_critico is not None else None,
        "dias_a_critico": float(dias_a_critico) if dias_a_critico is not None else None,

        # compat legacy
        "mm": float(mm_usada),
        "componente": "Cuchilla",
    }

    columnas = []
    valores = []

    for col in info:
        name = col["name"]
        if name == "id":
            continue

        val = base.get(name, None)

        # NOT NULL sin default → poner default seguro
        if (val is None) and col["notnull"] and (col["dflt"] is None):
            val = valor_default_por_tipo(col["type"])

        columnas.append(name)
        valores.append(val)

    placeholders = ", ".join(["?"] * len(columnas))
    cols_sql = ", ".join(columnas)

    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            f"INSERT INTO mediciones ({cols_sql}) VALUES ({placeholders})",
            tuple(valores)
        )
        con.commit()


def cargar_historial(limit: int = 300) -> pd.DataFrame:
    info = tabla_info("mediciones")
    cols = [c["name"] for c in info if c["name"] != "id"]

    preferidas = [
        "fecha", "equipo", "componente", "ubicacion", "usuario",
        "horometro", "mm", "mm_izq", "mm_der", "mm_usada",
        "condicion_pct", "estado", "tasa_mm_h", "horas_a_critico", "dias_a_critico",
    ]
    ordenadas = [c for c in preferidas if c in cols] + [c for c in cols if c not in preferidas]
    select_cols = ", ".join(ordenadas)

    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(
            f"""
            SELECT {select_cols}
            FROM mediciones
            ORDER BY datetime(fecha) DESC
            LIMIT {int(limit)}
            """,
            con
        )


def obtener_ultimas_mediciones_equipo(equipo: str, n: int = N_TASA) -> list[dict]:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT horometro, mm_usada
            FROM mediciones
            WHERE equipo = ?
              AND horometro IS NOT NULL
              AND mm_usada IS NOT NULL
            ORDER BY datetime(fecha) DESC
            LIMIT ?
        """, (equipo, n))
        rows = cur.fetchall()

    return [{"horometro": float(h), "mm_usada": float(mm)} for h, mm in rows]


# ==============================
# CÁLCULO
# ==============================

def regla_por_equipo(equipo: str) -> str:
    return "MOTONIVELADORA" if equipo in EQUIPOS_MOTONIVELADORA else "DOZER_854_D10_D11"


def interpolar_pct(mm: float, puntos: List[Tuple[float, float]]) -> float:
    puntos = sorted(puntos, key=lambda x: x[0])

    if mm <= puntos[0][0]:
        return float(puntos[0][1])
    if mm >= puntos[-1][0]:
        return float(puntos[-1][1])

    for (x1, y1), (x2, y2) in zip(puntos[:-1], puntos[1:]):
        if x1 <= mm <= x2:
            t = (mm - x1) / (x2 - x1)
            return float(y1 + t * (y2 - y1))

    return float(puntos[-1][1])


def clasificar_desgaste(desgaste_pct: float, umbrales: List[Tuple[str, float, str]]) -> tuple[str, str]:
    for estado, limite, accion in umbrales:
        if desgaste_pct >= limite:
            return estado, accion
    return "OK", "Operación normal."


def calcular_tasa_mm_h_promedio(meds: list[dict]) -> Optional[float]:
    """
    Tasa promedio (mm/h) usando tramos consecutivos válidos.
    Asume que el mm BAJA con el desgaste (mm_prev > mm_actual).
    """
    if len(meds) < 2:
        return None

    tasas = []
    # meds viene DESC: [más nueva, ..., más antigua]
    for i in range(len(meds) - 1):
        h_new, mm_new = meds[i]["horometro"], meds[i]["mm_usada"]
        h_old, mm_old = meds[i + 1]["horometro"], meds[i + 1]["mm_usada"]

        dh = h_new - h_old
        dmm = mm_old - mm_new  # positivo si bajó el mm

        if dh > 0 and dmm > 0:
            tasas.append(dmm / dh)

    if not tasas:
        return None

    return sum(tasas) / len(tasas)


def proyectar_a_critico(mm_usada: float, tasa_mm_h: Optional[float], mm_critico: float) -> tuple[Optional[float], Optional[float]]:
    if tasa_mm_h is None or tasa_mm_h <= 0:
        return None, None

    restante_mm = mm_usada - mm_critico
    if restante_mm <= 0:
        return 0.0, 0.0

    horas = restante_mm / tasa_mm_h
    dias = horas / HORAS_POR_DIA
    return round(horas, 1), round(dias, 1)


def evaluar(equipo: str, horometro: float, mm_izq: float, mm_der: float) -> Resultado:
    mm_usada = min(mm_izq, mm_der)

    regla = regla_por_equipo(equipo)
    cfg = REGLAS[regla]

    desgaste = float(interpolar_pct(mm_usada, cfg["puntos"]))
    estado, accion = clasificar_desgaste(desgaste, cfg["umbrales"])

    meds = [{"horometro": float(horometro), "mm_usada": float(mm_usada)}] + obtener_ultimas_mediciones_equipo(equipo, n=N_TASA)
    tasa_mm_h = calcular_tasa_mm_h_promedio(meds)

    horas_a_critico, dias_a_critico = proyectar_a_critico(mm_usada, tasa_mm_h, cfg["mm_critico"])

    return Resultado(
        mm_izq=mm_izq,
        mm_der=mm_der,
        mm_usada=mm_usada,
        desgaste_pct=round(desgaste, 1),
        estado=estado,
        accion=accion,
        horometro=horometro,
        tasa_mm_h=round(tasa_mm_h, 4) if tasa_mm_h is not None else None,
        horas_a_critico=horas_a_critico,
        dias_a_critico=dias_a_critico,
        regla=regla,
    )


# ==============================
# UI
# ==============================

st.set_page_config(page_title="Teck · GET Wear Monitor", layout="wide")

inject_teck_style()
init_db()
migrar_db_agregar_columnas()

render_header()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Ingreso de medición")

    equipo = st.selectbox("Equipo", EQUIPOS, index=0)
    ubicacion = st.text_input("Ubicación (opcional)", value="")
    usuario = st.text_input("Usuario (Técnico)", value="")

    st.divider()

    horometro = st.number_input("Horómetro", min_value=0.0, value=0.0, step=1.0)
    mm_izq = st.number_input("Medición Izquierda (mm)", min_value=0.0, value=190.0, step=0.1, format="%.2f")
    mm_der = st.number_input("Medición Derecha (mm)", min_value=0.0, value=190.0, step=0.1, format="%.2f")

    st.caption("Se usa automáticamente el valor MENOR (más crítico) para evaluar y proyectar.")

    if st.button("Evaluar y guardar", type="primary"):
        if not usuario.strip():
            st.error("Debes ingresar el nombre del técnico (Usuario).")
        elif horometro <= 0:
            st.error("Debes ingresar un horómetro válido (> 0).")
        else:
            res = evaluar(equipo, horometro, mm_izq, mm_der)
            cfg = REGLAS[res.regla]

            guardar_medicion(
                equipo=equipo,
                ubicacion=ubicacion,
                usuario=usuario,
                horometro=res.horometro,
                mm_izq=res.mm_izq,
                mm_der=res.mm_der,
                mm_usada=res.mm_usada,
                desgaste_pct=res.desgaste_pct,
                estado=res.estado,
                accion=res.accion,
                tasa_mm_h=res.tasa_mm_h,
                horas_a_critico=res.horas_a_critico,
                dias_a_critico=res.dias_a_critico,
            )

            st.success(f"Medición guardada correctamente. Regla aplicada: {res.regla}")

            st.metric("Mm usada (menor)", f"{res.mm_usada:.2f}")
            st.metric(cfg["label_pct"], f"{res.desgaste_pct:.1f}")
            st.metric("Estado", res.estado)
            st.write("Acción recomendada:", res.accion)

            if res.tasa_mm_h is None:
                st.info(
                    f"Tasa mm/h: sin datos suficientes (necesitas al menos 2 mediciones válidas). "
                    f"Promedio últimas {N_TASA} mediciones por equipo."
                )
            else:
                st.info(f"Tasa estimada (promedio): {res.tasa_mm_h} mm/h (mm bajando por desgaste)")

            if res.horas_a_critico is None:
                st.warning("Proyección a crítico: no disponible (sin tasa mm/h válida).")
            else:
                st.warning(f"Proyección a CRÍTICO (mm <= {cfg['mm_critico']}): ~{res.horas_a_critico} h (~{res.dias_a_critico} días)")

with col2:
    st.subheader("Historial de Mediciones")
    df = cargar_historial(limit=300)
    st.dataframe(df, width="stretch")