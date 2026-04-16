from __future__ import annotations

import io
import sqlite3
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional, Dict

import pandas as pd
import streamlit as st
from supabase import create_client

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ==============================
# ESTILO TECK
# ==============================

TECK_GREEN = "#007A3D"
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
        .cambio-box {{
            background: rgba(0,122,61,.15);
            border: 1px solid rgba(0,160,74,.4);
            border-radius: 12px;
            padding: 14px 16px;
            margin-top: 10px;
        }}
        .cambio-badge {{
            display: inline-block;
            background: linear-gradient(90deg, #007A3D, #00A04A);
            color: white;
            font-weight: 800;
            font-size: .8rem;
            padding: 3px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
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
    "201", "202", "203", "204", "205",
    "301", "302", "303",
]

EQUIPOS_MOTONIVELADORA = {"301", "302", "303"}

REF_WEEK_START = date(2026, 3, 5)
REF_WEEK_NUMBER = 10

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")

REGLAS: Dict[str, dict] = {
    "MOTONIVELADORA": {
        "puntos": [
            (122, 100), (145, 91), (167, 78), (190, 65),
            (212, 52), (235, 39), (257, 26), (280, 13), (302, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 90, "Cambiar cuchilla / condición inaceptable (rojo)."),
            ("MEDIO", 65, "Monitorear condición (amarillo)."),
            ("OK", 0, "Operación normal (verde)."),
        ],
        "mm_nuevo": 302.0,
        "mm_critico": 145.0,
        "label_pct": "Desgaste (%)",
    },
    "DOZER_854_D10_D11": {
        "puntos": [
            (75, 100), (82, 95), (83, 90), (100, 75),
            (140, 45), (170, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 95, "Detención inmediata."),
            ("ALTO", 75, "Programar cambio."),
            ("MEDIO", 45, "Monitorear condición."),
            ("OK", 0, "Operación normal."),
        ],
        "mm_nuevo": 170.0,
        "mm_critico": 82.0,
        "label_pct": "Desgaste (%)",
    },
}

HORAS_POR_DIA = 24
N_TASA = 5

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
# SEMANA
# ==============================

def calcular_semana_medicion(fecha_dt: datetime) -> tuple[int, str, date, date]:
    week_offset = (fecha_dt.date() - REF_WEEK_START).days // 7
    semana = REF_WEEK_NUMBER + week_offset
    inicio = REF_WEEK_START + timedelta(days=week_offset * 7)
    fin = inicio + timedelta(days=6)
    etiqueta = f"Semana {semana}"
    return semana, etiqueta, inicio, fin


# ==============================
# DB — ESQUEMA AMPLIADO
# ==============================

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        # Tabla principal de mediciones
        con.execute("""
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            equipo TEXT NOT NULL,
            ubicacion TEXT,
            usuario TEXT,
            componente TEXT,
            mm REAL,
            horometro REAL,
            mm_izq REAL,
            mm_der REAL,
            mm_usada REAL,
            condicion_pct REAL,
            estado TEXT,
            accion TEXT,
            tasa_mm_h REAL,
            horas_a_critico REAL,
            dias_a_critico REAL,
            semana_medicion INTEGER,
            semana_label TEXT,
            inicio_semana TEXT,
            fin_semana TEXT,
            es_cambio INTEGER DEFAULT 0
        )
        """)
        # ✅ NUEVA tabla de cambios de cuchilla
        con.execute("""
        CREATE TABLE IF NOT EXISTS cambios_cuchilla (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            equipo TEXT NOT NULL,
            horometro REAL NOT NULL,
            mm_izq_final REAL,
            mm_der_final REAL,
            fue_virada INTEGER DEFAULT 0,
            motivo TEXT,
            observaciones TEXT,
            tecnico_1 TEXT,
            tecnico_2 TEXT,
            usuario TEXT,
            semana_medicion INTEGER,
            semana_label TEXT
        )
        """)
        con.commit()


def migrar_db_agregar_columnas():
    with sqlite3.connect(DB_PATH) as con:
        cols = {row[1] for row in con.execute("PRAGMA table_info(mediciones)").fetchall()}
        faltantes = {
            "ubicacion": "ubicacion TEXT",
            "usuario": "usuario TEXT",
            "componente": "componente TEXT",
            "mm": "mm REAL",
            "horometro": "horometro REAL",
            "mm_izq": "mm_izq REAL",
            "mm_der": "mm_der REAL",
            "mm_usada": "mm_usada REAL",
            "condicion_pct": "condicion_pct REAL",
            "estado": "estado TEXT",
            "accion": "accion TEXT",
            "tasa_mm_h": "tasa_mm_h REAL",
            "horas_a_critico": "horas_a_critico REAL",
            "dias_a_critico": "dias_a_critico REAL",
            "semana_medicion": "semana_medicion INTEGER",
            "semana_label": "semana_label TEXT",
            "inicio_semana": "inicio_semana TEXT",
            "fin_semana": "fin_semana TEXT",
            "es_cambio": "es_cambio INTEGER DEFAULT 0",
        }
        for col, ddl in faltantes.items():
            if col not in cols:
                con.execute(f"ALTER TABLE mediciones ADD COLUMN {ddl}")
        con.commit()


def guardar_medicion(
    equipo, ubicacion, usuario, horometro,
    mm_izq, mm_der, mm_usada, desgaste_pct,
    estado, accion, tasa_mm_h, horas_a_critico, dias_a_critico,
):
    now = datetime.now()
    semana, semana_label, ini_sem, fin_sem = calcular_semana_medicion(now)
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO mediciones (
                fecha, equipo, ubicacion, usuario, componente, mm,
                horometro, mm_izq, mm_der, mm_usada,
                condicion_pct, estado, accion,
                tasa_mm_h, horas_a_critico, dias_a_critico,
                semana_medicion, semana_label, inicio_semana, fin_semana,
                es_cambio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            now.isoformat(timespec="seconds"), equipo,
            (ubicacion or "").strip() or None,
            (usuario or "").strip() or None,
            "Cuchilla", float(mm_usada), float(horometro),
            float(mm_izq), float(mm_der), float(mm_usada),
            float(desgaste_pct), estado, accion,
            float(tasa_mm_h) if tasa_mm_h is not None else None,
            float(horas_a_critico) if horas_a_critico is not None else None,
            float(dias_a_critico) if dias_a_critico is not None else None,
            int(semana), semana_label, ini_sem.isoformat(), fin_sem.isoformat(),
        ))
        con.commit()


def guardar_cambio_cuchilla(
    equipo: str,
    horometro: float,
    mm_izq_final: float,
    mm_der_final: float,
    fue_virada: bool,
    motivo: str,
    observaciones: str,
    tecnico_1: str,
    tecnico_2: str,
    usuario: str,
):
    """Registra un evento de cambio de cuchilla y reinicia el ciclo."""
    now = datetime.now()
    semana, semana_label, _, _ = calcular_semana_medicion(now)

    with sqlite3.connect(DB_PATH) as con:
        # 1. Guardar el evento de cambio
        con.execute("""
            INSERT INTO cambios_cuchilla (
                fecha, equipo, horometro, mm_izq_final, mm_der_final,
                fue_virada, motivo, observaciones,
                tecnico_1, tecnico_2, usuario,
                semana_medicion, semana_label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now.isoformat(timespec="seconds"),
            equipo, float(horometro),
            float(mm_izq_final), float(mm_der_final),
            1 if fue_virada else 0,
            motivo, observaciones,
            (tecnico_1 or "").strip() or None,
            (tecnico_2 or "").strip() or None,
            (usuario or "").strip() or None,
            int(semana), semana_label,
        ))

        # 2. Registrar medición de inicio de nuevo GET (mm_nuevo)
        regla = regla_por_equipo(equipo)
        cfg = REGLAS[regla]
        mm_nuevo = cfg["mm_nuevo"]

        con.execute("""
            INSERT INTO mediciones (
                fecha, equipo, usuario, componente, mm,
                horometro, mm_izq, mm_der, mm_usada,
                condicion_pct, estado, accion,
                semana_medicion, semana_label, es_cambio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            now.isoformat(timespec="seconds"),
            equipo,
            (tecnico_1 or usuario or "").strip() or None,
            "Cuchilla NUEVA",
            mm_nuevo, float(horometro),
            mm_nuevo, mm_nuevo, mm_nuevo,
            0.0, "OK", "GET nuevo instalado — iniciar monitoreo.",
            int(semana), semana_label,
        ))
        con.commit()


@st.cache_data(ttl=60)
def cargar_historial(limit: int = 500) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query(f"""
            SELECT id, fecha, semana_medicion, semana_label,
                   equipo, componente, ubicacion, usuario,
                   horometro, mm_usada, condicion_pct, estado,
                   tasa_mm_h, horas_a_critico, dias_a_critico,
                   es_cambio
            FROM mediciones
            WHERE semana_medicion IS NOT NULL
            ORDER BY datetime(fecha) DESC
            LIMIT {int(limit)}
        """, con)
    return df.loc[:, ~df.columns.duplicated()]


@st.cache_data(ttl=60)
def cargar_cambios() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query("""
            SELECT id, fecha, equipo, horometro,
                   mm_izq_final, mm_der_final,
                   fue_virada, motivo, observaciones,
                   tecnico_1, tecnico_2, usuario,
                   semana_label
            FROM cambios_cuchilla
            ORDER BY datetime(fecha) DESC
        """, con)
    return df


def obtener_ultimo_cambio_equipo(equipo: str) -> Optional[dict]:
    """Devuelve el último cambio de cuchilla para calcular vida útil del GET actual."""
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT fecha, horometro FROM cambios_cuchilla
            WHERE equipo = ?
            ORDER BY datetime(fecha) DESC LIMIT 1
        """, (equipo,))
        row = cur.fetchone()
    if row:
        return {"fecha": row[0], "horometro": float(row[1])}
    return None


def obtener_ultimas_mediciones_equipo(equipo: str, n: int = N_TASA) -> list[dict]:
    """Solo mediciones del ciclo actual (desde el último cambio)."""
    ultimo = obtener_ultimo_cambio_equipo(equipo)
    fecha_desde = ultimo["fecha"] if ultimo else "2000-01-01"

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT horometro, mm_usada
            FROM mediciones
            WHERE equipo = ?
              AND horometro IS NOT NULL
              AND mm_usada IS NOT NULL
              AND es_cambio = 0
              AND datetime(fecha) >= datetime(?)
            ORDER BY datetime(fecha) DESC
            LIMIT ?
        """, (equipo, fecha_desde, n))
        rows = cur.fetchall()
    return [{"horometro": float(h), "mm_usada": float(mm)} for h, mm in rows]


def eliminar_mediciones_por_ids(ids: list[int]) -> int:
    if not ids:
        return 0
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.executemany("DELETE FROM mediciones WHERE id = ?", [(int(i),) for i in ids])
        con.commit()
        return cur.rowcount


def eliminar_registros_prueba() -> int:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            DELETE FROM mediciones
            WHERE usuario IS NULL
               OR TRIM(usuario) = ''
               OR LOWER(TRIM(usuario)) IN (
                   'prueba','test','demo','usuario prueba',
                   'pajarraco medidor','cristian olivares'
               )
               OR semana_medicion IS NULL
        """)
        con.commit()
        return cur.rowcount


# ==============================
# CÁLCULO
# ==============================

def regla_por_equipo(equipo: str) -> str:
    return "MOTONIVELADORA" if equipo in EQUIPOS_MOTONIVELADORA else "DOZER_854_D10_D11"


def rango_regla(regla: str) -> tuple[float, float]:
    puntos = REGLAS[regla]["puntos"]
    xs = [p[0] for p in puntos]
    return min(xs), max(xs)


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


def clasificar_desgaste(desgaste_pct: float, umbrales) -> tuple[str, str]:
    for estado, limite, accion in umbrales:
        if desgaste_pct >= limite:
            return estado, accion
    return "OK", "Operación normal."


def calcular_tasa_mm_h_promedio(meds: list[dict]) -> Optional[float]:
    if len(meds) < 2:
        return None
    tasas = []
    for i in range(len(meds) - 1):
        h_new, mm_new = meds[i]["horometro"], meds[i]["mm_usada"]
        h_old, mm_old = meds[i + 1]["horometro"], meds[i + 1]["mm_usada"]
        dh = h_new - h_old
        dmm = mm_old - mm_new
        if dh > 0 and dmm > 0:
            tasas.append(dmm / dh)
    if not tasas:
        return None
    return sum(tasas) / len(tasas)


def proyectar_a_critico(mm_usada, tasa_mm_h, mm_critico) -> tuple[Optional[float], Optional[float]]:
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
    meds = [{"horometro": float(horometro), "mm_usada": float(mm_usada)}] + \
           obtener_ultimas_mediciones_equipo(equipo, n=N_TASA)
    tasa_mm_h = calcular_tasa_mm_h_promedio(meds)
    horas_a_critico, dias_a_critico = proyectar_a_critico(mm_usada, tasa_mm_h, cfg["mm_critico"])
    return Resultado(
        mm_izq=mm_izq, mm_der=mm_der, mm_usada=mm_usada,
        desgaste_pct=round(desgaste, 1), estado=estado, accion=accion,
        horometro=horometro,
        tasa_mm_h=round(tasa_mm_h, 4) if tasa_mm_h is not None else None,
        horas_a_critico=horas_a_critico, dias_a_critico=dias_a_critico,
        regla=regla,
    )


# ==============================
# REPORTES / KPI
# ==============================

def ultimos_estados_por_equipo(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df2 = df.copy()
    df2["fecha_dt"] = pd.to_datetime(df2["fecha"], errors="coerce")
    df2 = df2.sort_values("fecha_dt", ascending=False)
    return df2.drop_duplicates(subset=["equipo"], keep="first")


def generar_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ReporteSemanal")
    return output.getvalue()


def generar_resumen_mail(df: pd.DataFrame) -> str:
    if df.empty:
        return "Sin datos para el reporte semanal."
    ec = df["estado"].value_counts()
    return f"""Reporte semanal GET Wear Monitor
OK: {int(ec.get("OK", 0))}
Monitoreo: {int(ec.get("MEDIO", 0))}
Programar cambio: {int(ec.get("ALTO", 0))}
Crítico: {int(ec.get("CRÍTICO", 0))}""".strip()


# ==============================
# UI PRINCIPAL
# ==============================

st.set_page_config(page_title="Teck · GET Wear Monitor", layout="wide")
inject_teck_style()
init_db()
migrar_db_agregar_columnas()
render_header()

# Sidebar admin
with st.sidebar:
    st.subheader("Administración")
    admin_ok = False
    if ADMIN_PASSWORD:
        pwd = st.text_input("Clave administrador", type="password")
        admin_ok = (pwd == ADMIN_PASSWORD)
        if admin_ok:
            st.success("Modo administrador activo")
    else:
        st.info("Define ADMIN_PASSWORD en Secrets.")

# ─────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────
tab_medicion, tab_cambio, tab_historial, tab_cambios, tab_flota, tab_reporte = st.tabs([
    "📏 Ingreso Medición",
    "🔄 Cambio de Cuchilla",
    "📋 Historial",
    "🔧 Registro de Cambios",
    "🚛 Estado Flota",
    "📊 Reporte Semanal",
])

# ─────────────────────────────────────────────
# TAB 1: INGRESO DE MEDICIÓN
# ─────────────────────────────────────────────
with tab_medicion:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Ingreso de medición")

        equipo = st.selectbox("Equipo", EQUIPOS, index=0, key="eq_med")
        ubicacion = st.text_input("Ubicación (opcional)", value="", key="ub_med")
        usuario = st.text_input("Usuario (Técnico)", value="", key="us_med")
        st.divider()
        horometro = st.number_input("Horómetro", min_value=0.0, value=0.0, step=1.0, key="hr_med")

        regla_actual = regla_por_equipo(equipo)
        mm_max = REGLAS[regla_actual]["mm_nuevo"]

        mm_izq = st.number_input("Medición Izquierda (mm)", min_value=0.0, value=mm_max, step=0.1, format="%.2f", key="mi_med")
        mm_der = st.number_input("Medición Derecha (mm)", min_value=0.0, value=mm_max, step=0.1, format="%.2f", key="md_med")
        st.caption("Se usa automáticamente el valor MENOR (más crítico) para evaluar y proyectar.")

        # Info del ciclo actual
        ultimo_cambio = obtener_ultimo_cambio_equipo(equipo)
        if ultimo_cambio:
            st.info(f"📌 Último cambio de cuchilla: {ultimo_cambio['fecha'][:10]} · Horómetro: {ultimo_cambio['horometro']:,.0f} hrs")
        else:
            st.caption("ℹ️ Sin cambio de cuchilla registrado. La tasa usa todo el historial.")

        if st.button("Evaluar y guardar", type="primary", key="btn_med"):
            if not usuario.strip():
                st.error("Debes ingresar el nombre del técnico.")
            elif horometro <= 0:
                st.error("Debes ingresar un horómetro válido (> 0).")
            else:
                regla = regla_por_equipo(equipo)
                mm_min_val, mm_max_val = rango_regla(regla)
                errores = []
                if not (mm_min_val <= mm_izq <= mm_max_val):
                    errores.append(f"Medición izquierda fuera de rango ({mm_min_val}–{mm_max_val} mm).")
                if not (mm_min_val <= mm_der <= mm_max_val):
                    errores.append(f"Medición derecha fuera de rango ({mm_min_val}–{mm_max_val} mm).")
                if errores:
                    for e in errores:
                        st.error(e)
                    st.stop()

                res = evaluar(equipo, horometro, mm_izq, mm_der)
                cfg = REGLAS[res.regla]
                semana, semana_label, ini_sem, fin_sem = calcular_semana_medicion(datetime.now())

                guardar_medicion(
                    equipo=equipo, ubicacion=ubicacion, usuario=usuario,
                    horometro=res.horometro, mm_izq=res.mm_izq, mm_der=res.mm_der,
                    mm_usada=res.mm_usada, desgaste_pct=res.desgaste_pct,
                    estado=res.estado, accion=res.accion,
                    tasa_mm_h=res.tasa_mm_h,
                    horas_a_critico=res.horas_a_critico,
                    dias_a_critico=res.dias_a_critico,
                )
                cargar_historial.clear()

                color_estado = {"OK": "🟢", "MEDIO": "🟡", "ALTO": "🟠", "CRÍTICO": "🔴"}.get(res.estado, "⚪")
                st.success(f"✅ Medición guardada · {semana_label} ({ini_sem} → {fin_sem})")
                st.metric("Mm usada (menor)", f"{res.mm_usada:.2f}")
                st.metric(cfg["label_pct"], f"{res.desgaste_pct:.1f}%")
                st.metric("Estado", f"{color_estado} {res.estado}")
                st.write("**Acción recomendada:**", res.accion)

                if res.tasa_mm_h is None:
                    st.info(f"Tasa mm/h: sin datos suficientes (mínimo 2 mediciones en el ciclo actual).")
                else:
                    st.info(f"Tasa estimada: **{res.tasa_mm_h} mm/h**")

                if res.horas_a_critico is None:
                    st.warning("Proyección a crítico: no disponible (se necesita tasa calculada).")
                else:
                    st.warning(
                        f"⏱ Proyección a crítico (≤{cfg['mm_critico']} mm): "
                        f"~**{res.horas_a_critico} h** (~**{res.dias_a_critico} días**)"
                    )

    with col2:
        st.subheader("Historial de Mediciones")
        df_hist = cargar_historial(limit=500)
        if not df_hist.empty:
            # Filtrar solo el equipo seleccionado
            df_eq = df_hist[df_hist["equipo"] == equipo].head(20)
            if not df_eq.empty:
                st.dataframe(df_eq.drop(columns=["id"], errors="ignore"), use_container_width=True)
            else:
                st.info(f"Sin mediciones para equipo {equipo}.")
        else:
            st.info("Sin mediciones aún.")


# ─────────────────────────────────────────────
# TAB 2: CAMBIO DE CUCHILLA ← NUEVO
# ─────────────────────────────────────────────
with tab_cambio:
    st.subheader("🔄 Registro de Cambio de Cuchilla / GET")
    st.caption(
        "Completa este formulario al instalar un GET nuevo. "
        "Se registrará la medición final de la cuchilla retirada y se iniciará un ciclo de desgaste nuevo."
    )

    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.markdown("#### Datos del equipo")
        eq_cambio = st.selectbox("Equipo", EQUIPOS, key="eq_cambio")
        hr_cambio = st.number_input("Horómetro al momento del cambio", min_value=0.0, value=0.0, step=1.0, key="hr_cambio")

        regla_cambio = regla_por_equipo(eq_cambio)
        mm_max_cambio = REGLAS[regla_cambio]["mm_nuevo"]
        mm_critico_cambio = REGLAS[regla_cambio]["mm_critico"]

        st.markdown("#### Medición final del GET retirado")
        mm_izq_final = st.number_input(
            "Altura cuchilla IZQUIERDA al retiro (mm)",
            min_value=0.0, max_value=float(mm_max_cambio),
            value=float(mm_critico_cambio), step=0.1, format="%.1f",
            key="mi_cambio"
        )
        mm_der_final = st.number_input(
            "Altura cuchilla DERECHA al retiro (mm)",
            min_value=0.0, max_value=float(mm_max_cambio),
            value=float(mm_critico_cambio), step=0.1, format="%.1f",
            key="md_cambio"
        )

        fue_virada = st.radio(
            "¿La cuchilla fue virada antes del cambio?",
            options=["NO", "SÍ"],
            horizontal=True,
            key="virada_cambio"
        )

        motivo = st.selectbox(
            "Motivo del cambio",
            options=[
                "Desgaste normal (límite alcanzado)",
                "Cambio preventivo (programado)",
                "Daño / impacto",
                "Cambio por campaña de mantenimiento",
                "Otro",
            ],
            key="motivo_cambio"
        )

    with c2:
        st.markdown("#### Técnicos participantes")
        tecnico_1 = st.text_input("Técnico 1 (nombre y apellido)", key="tec1_cambio")
        tecnico_2 = st.text_input("Técnico 2 (nombre y apellido, opcional)", key="tec2_cambio")

        st.markdown("#### Observaciones generales")
        observaciones = st.text_area(
            "OT generadas / actividades adicionales / aspectos de seguridad / anomalías",
            height=120,
            key="obs_cambio"
        )

        st.markdown("#### Autorización")
        supervisor = st.text_input("Usuario que registra (supervisor / técnico líder)", key="sup_cambio")

        st.divider()

        # Preview del nuevo ciclo
        st.markdown("**ℹ️ Al confirmar el cambio:**")
        st.markdown(
            f"- Se registrará la medición final del GET retirado\n"
            f"- Se iniciará ciclo nuevo con **{mm_max_cambio:.0f} mm** (GET nuevo)\n"
            f"- La tasa de desgaste se calculará desde este horómetro en adelante"
        )

        if st.button("✅ Confirmar cambio de cuchilla", type="primary", key="btn_cambio"):
            errores = []
            if hr_cambio <= 0:
                errores.append("Horómetro debe ser mayor que 0.")
            if not tecnico_1.strip():
                errores.append("Debe ingresar al menos el Técnico 1.")
            if not supervisor.strip():
                errores.append("Debe ingresar el usuario que registra.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                guardar_cambio_cuchilla(
                    equipo=eq_cambio,
                    horometro=hr_cambio,
                    mm_izq_final=mm_izq_final,
                    mm_der_final=mm_der_final,
                    fue_virada=(fue_virada == "SÍ"),
                    motivo=motivo,
                    observaciones=observaciones,
                    tecnico_1=tecnico_1,
                    tecnico_2=tecnico_2,
                    usuario=supervisor,
                )
                cargar_historial.clear()
                cargar_cambios.clear()

                st.success(
                    f"🔄 Cambio de cuchilla registrado para Equipo **{eq_cambio}** "
                    f"· Horómetro: **{hr_cambio:,.0f} hrs**\n\n"
                    f"Ciclo nuevo iniciado con GET de **{mm_max_cambio:.0f} mm**."
                )
                st.balloons()


# ─────────────────────────────────────────────
# TAB 3: HISTORIAL COMPLETO
# ─────────────────────────────────────────────
with tab_historial:
    st.subheader("Historial de Mediciones")
    df_h = cargar_historial(limit=500)

    if not df_h.empty:
        # Filtros
        fc1, fc2 = st.columns(2)
        with fc1:
            eq_filtro = st.multiselect("Filtrar por equipo", options=sorted(df_h["equipo"].unique()), default=[])
        with fc2:
            estado_filtro = st.multiselect("Filtrar por estado", options=sorted(df_h["estado"].dropna().unique()), default=[])

        df_show = df_h.copy()
        if eq_filtro:
            df_show = df_show[df_show["equipo"].isin(eq_filtro)]
        if estado_filtro:
            df_show = df_show[df_show["estado"].isin(estado_filtro)]

        st.dataframe(df_show.drop(columns=["id"], errors="ignore"), use_container_width=True)

        if admin_ok and "id" in df_h.columns:
            st.markdown("### Eliminar registro")
            df_del = df_h[["id", "fecha", "equipo", "usuario", "estado"]].copy()
            df_del["desc"] = df_del.apply(
                lambda r: f"ID {int(r['id'])} | {r['fecha']} | Eq {r['equipo']} | {r['usuario']} | {r['estado']}", axis=1
            )
            sel = st.selectbox("Seleccionar registro", [""] + df_del["desc"].tolist())
            if sel:
                id_borrar = int(sel.split("|")[0].replace("ID", "").strip())
                if st.button("Eliminar registro seleccionado", type="primary"):
                    n = eliminar_mediciones_por_ids([id_borrar])
                    st.success(f"Se eliminaron {n} medición(es).")
                    cargar_historial.clear()
                    st.rerun()
    else:
        st.info("Sin mediciones aún.")


# ─────────────────────────────────────────────
# TAB 4: REGISTRO DE CAMBIOS ← NUEVO
# ─────────────────────────────────────────────
with tab_cambios:
    st.subheader("🔧 Historial de Cambios de Cuchilla")
    df_cambios = cargar_cambios()

    if not df_cambios.empty:
        # Renombrar columnas para display
        df_display = df_cambios.copy()
        df_display["fue_virada"] = df_display["fue_virada"].map({1: "SÍ", 0: "NO"})
        df_display = df_display.rename(columns={
            "fecha": "Fecha", "equipo": "Equipo", "horometro": "Horómetro",
            "mm_izq_final": "IZQ final (mm)", "mm_der_final": "DER final (mm)",
            "fue_virada": "Fue virada", "motivo": "Motivo",
            "observaciones": "Observaciones", "tecnico_1": "Técnico 1",
            "tecnico_2": "Técnico 2", "usuario": "Registrado por",
            "semana_label": "Semana",
        })
        st.dataframe(
            df_display.drop(columns=["id"], errors="ignore"),
            use_container_width=True
        )

        # KPIs de cambios
        st.divider()
        st.markdown("#### Resumen por equipo")
        resumen = df_cambios.groupby("equipo").agg(
            total_cambios=("id", "count"),
            ultimo_cambio=("fecha", "max"),
            ultimo_horometro=("horometro", "max"),
        ).reset_index()
        st.dataframe(resumen, use_container_width=True)

        # Descarga Excel
        st.download_button(
            "⬇️ Descargar historial de cambios Excel",
            data=generar_excel_bytes(df_display.drop(columns=["id"], errors="ignore")),
            file_name="cambios_cuchilla.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Sin cambios de cuchilla registrados aún.")


# ─────────────────────────────────────────────
# TAB 5: ESTADO DE FLOTA
# ─────────────────────────────────────────────
with tab_flota:
    st.subheader("Estado de flota")
    df_flot = cargar_historial(limit=5000)
    ultimos_flot = ultimos_estados_por_equipo(df_flot) if not df_flot.empty else pd.DataFrame()

    if not ultimos_flot.empty:
        ec = ultimos_flot["estado"].value_counts()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🟢 OK", int(ec.get("OK", 0)))
        k2.metric("🟡 Monitoreo", int(ec.get("MEDIO", 0)))
        k3.metric("🟠 Programar cambio", int(ec.get("ALTO", 0)))
        k4.metric("🔴 Crítico", int(ec.get("CRÍTICO", 0)))

        st.divider()
        st.subheader("Ranking de desgaste por equipo")
        if "condicion_pct" in ultimos_flot.columns:
            ranking = ultimos_flot[["equipo", "condicion_pct"]].copy()
            ranking = ranking.sort_values("condicion_pct", ascending=False)
            ranking = ranking.rename(columns={"condicion_pct": "desgaste_pct"})
            st.bar_chart(ranking.set_index("equipo"))
            st.dataframe(ranking, use_container_width=True)

        st.divider()
        st.subheader("Proyección de cambio")
        cols_proj = [c for c in ["equipo", "mm_usada", "estado", "tasa_mm_h", "horas_a_critico", "dias_a_critico"] if c in ultimos_flot.columns]
        proy = ultimos_flot[cols_proj].copy()
        if "horas_a_critico" in proy.columns:
            proy = proy.sort_values("horas_a_critico", na_position="last")
        st.dataframe(proy, use_container_width=True)
    else:
        st.info("Sin datos para estado de flota.")


# ─────────────────────────────────────────────
# TAB 6: REPORTE SEMANAL
# ─────────────────────────────────────────────
with tab_reporte:
    st.subheader("Reporte semanal")
    df_all = cargar_historial(limit=5000)

    if not df_all.empty and "semana_medicion" in df_all.columns:
        semanas_disp = sorted(df_all["semana_medicion"].dropna().astype(int).unique().tolist(), reverse=True)
        if semanas_disp:
            semana_sel = st.selectbox("Semana a reportar", semanas_disp)
            eq_disp = ["TODOS"] + sorted(df_all["equipo"].dropna().astype(str).unique().tolist())
            eq_sel = st.selectbox("Equipo", eq_disp)

            df_sem = df_all[df_all["semana_medicion"] == semana_sel].copy()
            if eq_sel != "TODOS":
                df_sem = df_sem[df_sem["equipo"].astype(str) == eq_sel].copy()

            df_rep = df_sem.copy()
            df_rep["criticidad"] = df_rep["condicion_pct"]
            cols_rep = ["equipo", "semana_medicion", "usuario", "horometro", "criticidad", "estado"]
            cols_rep = [c for c in cols_rep if c in df_rep.columns]
            df_rep = df_rep[cols_rep]

            st.download_button(
                "⬇️ Descargar reporte semanal Excel",
                data=generar_excel_bytes(df_rep),
                file_name=f"reporte_semana_{semana_sel}_{eq_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.text_area(
                "Resumen para correo",
                value=generar_resumen_mail(ultimos_estados_por_equipo(df_sem)),
                height=150
            )
        else:
            st.info("No hay semanas válidas para reportar.")
    else:
        st.info("Sin datos suficientes para reporte semanal.")

    # Administración
    st.divider()
    st.subheader("Administración de datos")
    if admin_ok:
        with open(DB_PATH, "rb") as f:
            st.download_button(
                "⬇️ Descargar base de datos SQLite",
                data=f.read(),
                file_name="mediciones.db",
                mime="application/octet-stream"
            )
        if st.button("🗑️ Eliminar registros de prueba"):
            n = eliminar_registros_prueba()
            st.success(f"Se eliminaron {n} registros de prueba.")
            cargar_historial.clear()
            st.rerun()
    else:
        st.info("Descarga de base y eliminaciones solo para administrador.")

st.caption(
    "⚠️ Nota: El envío automático de correo los miércoles requiere Power Automate o programador externo. "
    "| Persistencia de datos: Para producción migrar a Supabase (PostgreSQL)."
)
