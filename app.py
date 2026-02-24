from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional

import pandas as pd
import streamlit as st


# ==============================
# CONFIG (AJUSTABLE)
# ==============================

DB_PATH = "mediciones.db"

# Lista de equipos (AJUSTAR a tu listado real)
EQUIPOS = [
    "101", "102", "103", "104", "105", "106", "108",
    "201", "202", "203", "204",
    "301", "302", "303",
]

# Tabla mm vs % condición (tu lámina)
PUNTOS: List[Tuple[float, float]] = [
    (122, 100),
    (145, 91),
    (167, 78),
    (190, 65),
    (212, 52),
    (235, 39),
    (257, 26),
    (280, 13),
    (302, 0),
]

# Semáforo por % condición (menor = peor)
UMBRALES = [
    ("CRÍTICO", 13),
    ("ALTO", 26),
    ("MEDIO", 52),
    ("OK", 100),
]

# Umbral crítico para proyección (mm)
UMBRAL_CRITICO_MM = 280

# Conversión horas->días para mostrar proyección
HORAS_POR_DIA = 24


# ==============================
# MODELO
# ==============================

@dataclass
class Resultado:
    mm_izq: float
    mm_der: float
    mm_usada: float  # menor
    condicion_pct: float
    estado: str
    accion: str
    horometro: float
    tasa_mm_h: Optional[float]
    horas_a_critico: Optional[float]
    dias_a_critico: Optional[float]


# ==============================
# DB
# ==============================

def init_db():
    """
    Crea tabla (si no existe) con el esquema NUEVO.
    Si ya existía una tabla antigua, esto no la modifica: para eso está migrar_db().
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
    Si venías con la DB antigua (sin horometro/mm_izq/mm_der/mm_usada),
    agrega las columnas faltantes sin borrar datos.
    """
    with sqlite3.connect(DB_PATH) as con:
        cols = {row[1] for row in con.execute("PRAGMA table_info(mediciones)").fetchall()}

        def add(sql_col: str):
            con.execute(f"ALTER TABLE mediciones ADD COLUMN {sql_col}")

        # Columnas nuevas (si faltan)
        if "horometro" not in cols: add("horometro REAL")
        if "mm_izq" not in cols: add("mm_izq REAL")
        if "mm_der" not in cols: add("mm_der REAL")
        if "mm_usada" not in cols: add("mm_usada REAL")

        if "tasa_mm_h" not in cols: add("tasa_mm_h REAL")
        if "horas_a_critico" not in cols: add("horas_a_critico REAL")
        if "dias_a_critico" not in cols: add("dias_a_critico REAL")

        con.commit()


def guardar_medicion(
    equipo: str,
    ubicacion: Optional[str],
    usuario: Optional[str],
    horometro: float,
    mm_izq: float,
    mm_der: float,
    mm_usada: float,
    condicion_pct: float,
    estado: str,
    accion: str,
    tasa_mm_h: Optional[float],
    horas_a_critico: Optional[float],
    dias_a_critico: Optional[float],
):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        INSERT INTO mediciones (
            fecha, equipo, ubicacion, usuario,
            horometro, mm_izq, mm_der, mm_usada,
            condicion_pct, estado, accion,
            tasa_mm_h, horas_a_critico, dias_a_critico
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            equipo,
            (ubicacion or "").strip() or None,
            (usuario or "").strip() or None,
            float(horometro),
            float(mm_izq),
            float(mm_der),
            float(mm_usada),
            float(condicion_pct),
            estado,
            accion,
            float(tasa_mm_h) if tasa_mm_h is not None else None,
            float(horas_a_critico) if horas_a_critico is not None else None,
            float(dias_a_critico) if dias_a_critico is not None else None,
        ))
        con.commit()


def cargar_historial(limit: int = 300) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(
            f"""
            SELECT
                fecha, equipo, ubicacion, usuario,
                horometro, mm_izq, mm_der, mm_usada,
                condicion_pct, estado,
                tasa_mm_h, horas_a_critico, dias_a_critico
            FROM mediciones
            ORDER BY datetime(fecha) DESC
            LIMIT {int(limit)}
            """,
            con
        )


def obtener_ultima_medicion_equipo(equipo: str) -> Optional[dict]:
    """
    Trae la última medición guardada para ese equipo (para calcular tasa).
    """
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT horometro, mm_usada
            FROM mediciones
            WHERE equipo = ?
            ORDER BY datetime(fecha) DESC
            LIMIT 1
        """, (equipo,))
        row = cur.fetchone()
        if not row or row[0] is None or row[1] is None:
            return None
        return {"horometro": float(row[0]), "mm_usada": float(row[1])}


# ==============================
# CÁLCULO
# ==============================

def interpolar_condicion(mm: float, puntos=PUNTOS) -> float:
    puntos = sorted(puntos, key=lambda x: x[0])

    if mm <= puntos[0][0]:
        return puntos[0][1]
    if mm >= puntos[-1][0]:
        return puntos[-1][1]

    for (x1, y1), (x2, y2) in zip(puntos[:-1], puntos[1:]):
        if x1 <= mm <= x2:
            t = (mm - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)

    return puntos[-1][1]


def clasificar(cond_pct: float) -> tuple[str, str]:
    for estado, limite in UMBRALES:
        if cond_pct <= limite:
            if estado == "CRÍTICO":
                return estado, "Cambiar cuchilla inmediatamente."
            if estado == "ALTO":
                return estado, "Programar cambio y aumentar frecuencia de medición."
            if estado == "MEDIO":
                return estado, "Monitorear condición."
            return estado, "Operación normal."
    return "OK", "Operación normal."


def calcular_tasa_mm_h(prev: Optional[dict], horometro: float, mm_usada: float) -> Optional[float]:
    """
    tasa mm/h = (mm_actual - mm_prev) / (h_actual - h_prev)
    Si dh <= 0 o dmm < 0 (posible cambio de cuchilla o error), no calcula.
    """
    if not prev:
        return None

    h_prev = prev["horometro"]
    mm_prev = prev["mm_usada"]
    dh = horometro - h_prev
    dmm = mm_usada - mm_prev

    if dh <= 0:
        return None
    if dmm < 0:
        return None

    return dmm / dh


def proyectar_a_critico(mm_usada: float, tasa_mm_h: Optional[float]) -> tuple[Optional[float], Optional[float]]:
    if tasa_mm_h is None or tasa_mm_h <= 0:
        return None, None

    restante_mm = UMBRAL_CRITICO_MM - mm_usada
    if restante_mm <= 0:
        return 0.0, 0.0

    horas = restante_mm / tasa_mm_h
    dias = horas / HORAS_POR_DIA
    return round(horas, 1), round(dias, 1)


def evaluar(equipo: str, horometro: float, mm_izq: float, mm_der: float) -> Resultado:
    mm_usada = min(mm_izq, mm_der)  # la menor manda
    cond = float(interpolar_condicion(mm_usada))
    estado, accion = clasificar(cond)

    prev = obtener_ultima_medicion_equipo(equipo)
    tasa_mm_h = calcular_tasa_mm_h(prev, horometro, mm_usada)
    horas_a_critico, dias_a_critico = proyectar_a_critico(mm_usada, tasa_mm_h)

    return Resultado(
        mm_izq=mm_izq,
        mm_der=mm_der,
        mm_usada=mm_usada,
        condicion_pct=round(cond, 1),
        estado=estado,
        accion=accion,
        horometro=horometro,
        tasa_mm_h=round(tasa_mm_h, 4) if tasa_mm_h is not None else None,
        horas_a_critico=horas_a_critico,
        dias_a_critico=dias_a_critico,
    )


# ==============================
# UI
# ==============================

st.set_page_config(page_title="GET - Medición", layout="wide")

init_db()
migrar_db_agregar_columnas()

st.title("GET - Manual de Medición de Desgaste")

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

            guardar_medicion(
                equipo=equipo,
                ubicacion=ubicacion,
                usuario=usuario,
                horometro=res.horometro,
                mm_izq=res.mm_izq,
                mm_der=res.mm_der,
                mm_usada=res.mm_usada,
                condicion_pct=res.condicion_pct,
                estado=res.estado,
                accion=res.accion,
                tasa_mm_h=res.tasa_mm_h,
                horas_a_critico=res.horas_a_critico,
                dias_a_critico=res.dias_a_critico,
            )

            st.success("Medición guardada correctamente.")

            st.metric("Mm usada (menor)", f"{res.mm_usada:.2f}")
            st.metric("Condición (%)", f"{res.condicion_pct:.1f}")
            st.metric("Estado", res.estado)
            st.write("Acción recomendada:", res.accion)

            if res.tasa_mm_h is None:
                st.info("Tasa mm/h: sin datos suficientes (necesitas al menos 2 mediciones con horómetro creciente).")
            else:
                st.info(f"Tasa estimada: {res.tasa_mm_h} mm/h")

            if res.horas_a_critico is None:
                st.warning("Proyección a crítico: no disponible (sin tasa mm/h válida).")
            else:
                st.warning(f"Proyección a CRÍTICO ({UMBRAL_CRITICO_MM} mm): ~{res.horas_a_critico} h (~{res.dias_a_critico} días)")

with col2:
    st.subheader("Historial de Mediciones")
    df = cargar_historial(limit=300)
    st.dataframe(df, width="stretch")