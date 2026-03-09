from __future__ import annotations

import io
import sqlite3
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional, Dict

import pandas as pd
import streamlit as st


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
            (75, 100),
            (82, 95),
            (83, 90),
            (100, 75),
            (140, 45),
            (170, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 95, "Detención inmediata."),
            ("ALTO", 75, "Programar cambio."),
            ("MEDIO", 45, "Monitorear condición."),
            ("OK", 0, "Operación normal."),
        ],
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
# SEMANA DE MEDICIÓN
# ==============================

def calcular_semana_medicion(fecha_dt: datetime) -> tuple[int, str, date, date]:
    week_offset = (fecha_dt.date() - REF_WEEK_START).days // 7
    semana = REF_WEEK_NUMBER + week_offset
    inicio = REF_WEEK_START + timedelta(days=week_offset * 7)
    fin = inicio + timedelta(days=6)
    etiqueta = f"Semana {semana}"
    return semana, etiqueta, inicio, fin


# ==============================
# DB
# ==============================

def init_db():
    with sqlite3.connect(DB_PATH) as con:
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
            fin_semana TEXT
        )
        """)
        con.commit()


def migrar_db_agregar_columnas():
    with sqlite3.connect(DB_PATH) as con:
        cols = {row[1] for row in con.execute("PRAGMA table_info(mediciones)").fetchall()}

        def add(sql_col: str):
            con.execute(f"ALTER TABLE mediciones ADD COLUMN {sql_col}")

        faltantes = {
            "fecha": "fecha TEXT",
            "equipo": "equipo TEXT",
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
        }

        for col, ddl in faltantes.items():
            if col not in cols:
                add(ddl)

        con.commit()


def tabla_info(tabla: str) -> list[dict]:
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(f"PRAGMA table_info({tabla})").fetchall()
    return [
        {"name": r[1], "type": (r[2] or "").upper(), "notnull": bool(r[3]), "dflt": r[4]}
        for r in rows
    ]


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
    now = datetime.now()
    semana, semana_label, inicio_sem, fin_sem = calcular_semana_medicion(now)

    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO mediciones (
                fecha, equipo, ubicacion, usuario, componente, mm,
                horometro, mm_izq, mm_der, mm_usada,
                condicion_pct, estado, accion,
                tasa_mm_h, horas_a_critico, dias_a_critico,
                semana_medicion, semana_label, inicio_semana, fin_semana
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now.isoformat(timespec="seconds"),
            equipo,
            (ubicacion or "").strip() or None,
            (usuario or "").strip() or None,
            "Cuchilla",
            float(mm_usada),
            float(horometro),
            float(mm_izq),
            float(mm_der),
            float(mm_usada),
            float(desgaste_pct),
            estado,
            accion,
            float(tasa_mm_h) if tasa_mm_h is not None else None,
            float(horas_a_critico) if horas_a_critico is not None else None,
            float(dias_a_critico) if dias_a_critico is not None else None,
            int(semana),
            semana_label,
            inicio_sem.isoformat(),
            fin_sem.isoformat(),
        ))
        con.commit()


def cargar_historial(limit: int = 500) -> pd.DataFrame:
    info = tabla_info("mediciones")
    cols = [c["name"] for c in info if c["name"] != "id"]

    preferidas = [
        "id", "fecha", "semana_medicion", "semana_label",
        "equipo", "componente", "ubicacion", "usuario",
        "horometro", "mm", "mm_izq", "mm_der", "mm_usada",
        "condicion_pct", "estado", "tasa_mm_h",
        "horas_a_critico", "dias_a_critico", "accion"
    ]

    ordenadas = []
    usadas = set()
    for c in preferidas + cols:
        if c in cols and c not in usadas:
            ordenadas.append(c)
            usadas.add(c)

    select_cols = ", ".join(ordenadas)

    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query(
            f"""
            SELECT {select_cols}
            FROM mediciones
            ORDER BY datetime(fecha) DESC
            LIMIT {int(limit)}
            """,
            con
        )

    df = df.loc[:, ~df.columns.duplicated()]
    return df


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
                   'prueba', 'test', 'demo', 'usuario prueba',
                   'pajarraco medidor', 'cristian olivares'
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


def clasificar_desgaste(desgaste_pct: float, umbrales: List[Tuple[str, float, str]]) -> tuple[str, str]:
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

    estado_counts = df["estado"].value_counts()
    ok = int(estado_counts.get("OK", 0))
    monitoreo = int(estado_counts.get("MEDIO", 0))
    programar = int(estado_counts.get("ALTO", 0))
    critico = int(estado_counts.get("CRÍTICO", 0))

    resumen = f"""
Reporte semanal GET Wear Monitor

Estado de flota:
OK: {ok}
Monitoreo: {monitoreo}
Programar cambio: {programar}
Crítico: {critico}
"""
    return resumen.strip()


# ==============================
# UI
# ==============================

st.set_page_config(page_title="Teck · GET Wear Monitor", layout="wide")

inject_teck_style()
init_db()
migrar_db_agregar_columnas()
render_header()

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

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Ingreso de medición")

    equipo = st.selectbox("Equipo", EQUIPOS, index=0)
    ubicacion = st.text_input("Ubicación (opcional)", value="")
    usuario = st.text_input("Usuario (Técnico)", value="")

    st.divider()

    horometro = st.number_input("Horómetro", min_value=0.0, value=0.0, step=1.0)
    mm_izq = st.number_input("Medición Izquierda (mm)", min_value=0.0, value=170.0, step=0.1, format="%.2f")
    mm_der = st.number_input("Medición Derecha (mm)", min_value=0.0, value=170.0, step=0.1, format="%.2f")

    st.caption("Se usa automáticamente el valor MENOR (más crítico) para evaluar y proyectar.")

    if st.button("Evaluar y guardar", type="primary"):
        if not usuario.strip():
            st.error("Debes ingresar el nombre del técnico.")
        elif horometro <= 0:
            st.error("Debes ingresar un horómetro válido (> 0).")
        else:
            regla = regla_por_equipo(equipo)
            mm_min, mm_max = rango_regla(regla)

            errores = []
            if not (mm_min <= mm_izq <= mm_max):
                errores.append(f"Medición izquierda fuera de rango permitido ({mm_min} a {mm_max} mm).")
            if not (mm_min <= mm_der <= mm_max):
                errores.append(f"Medición derecha fuera de rango permitido ({mm_min} a {mm_max} mm).")

            if errores:
                for e in errores:
                    st.error(e)
                st.stop()

            res = evaluar(equipo, horometro, mm_izq, mm_der)
            cfg = REGLAS[res.regla]
            semana, semana_label, ini_sem, fin_sem = calcular_semana_medicion(datetime.now())

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

            st.success(f"Medición guardada correctamente. Regla aplicada: {res.regla} · {semana_label} ({ini_sem} a {fin_sem})")
            st.metric("Mm usada (menor)", f"{res.mm_usada:.2f}")
            st.metric(cfg["label_pct"], f"{res.desgaste_pct:.1f}")
            st.metric("Estado", res.estado)
            st.write("Acción recomendada:", res.accion)

            if res.tasa_mm_h is None:
                st.info(f"Tasa mm/h: sin datos suficientes. Promedio últimas {N_TASA} mediciones por equipo.")
            else:
                st.info(f"Tasa estimada (promedio): {res.tasa_mm_h} mm/h")

            if res.horas_a_critico is None:
                st.warning("Proyección a crítico: no disponible.")
            else:
                st.warning(f"Proyección a crítico (mm <= {cfg['mm_critico']}): ~{res.horas_a_critico} h (~{res.dias_a_critico} días)")

with col2:
    st.subheader("Historial de Mediciones")
    df = cargar_historial(limit=500)

    if not df.empty:
        df_hist = df.copy()
        df_hist = df_hist.loc[:, ~df_hist.columns.duplicated()]

        st.dataframe(df_hist, width="stretch")

        if admin_ok and "id" in df_hist.columns:
            st.markdown("### Eliminar registros del historial")

            df_delete = df_hist[["id", "fecha", "equipo", "usuario", "estado"]].copy()
            df_delete["descripcion"] = df_delete.apply(
                lambda r: f"ID {int(r['id'])} | {r['fecha']} | Eq {r['equipo']} | {r['usuario']} | {r['estado']}",
                axis=1
            )

            seleccion = st.multiselect(
                "Selecciona registros a eliminar",
                options=df_delete["descripcion"].tolist()
            )

            if len(seleccion) > 0:
                ids_borrar = df_delete[df_delete["descripcion"].isin(seleccion)]["id"].astype(int).tolist()
                st.warning(f"Se eliminarán {len(ids_borrar)} registro(s).")

                if st.button("Eliminar registros seleccionados", type="primary"):
                    borradas = eliminar_mediciones_por_ids(ids_borrar)
                    st.success(f"Se eliminaron {borradas} medición(es).")
                    st.rerun()
    else:
        st.info("Sin mediciones aún.")


st.divider()
st.subheader("Estado de flota")

df_flot = cargar_historial(limit=5000)
ultimos_flot = ultimos_estados_por_equipo(df_flot) if not df_flot.empty else pd.DataFrame()

if not ultimos_flot.empty:
    estado_counts = ultimos_flot["estado"].value_counts()
    ok = int(estado_counts.get("OK", 0))
    monitoreo = int(estado_counts.get("MEDIO", 0))
    programar = int(estado_counts.get("ALTO", 0))
    critico = int(estado_counts.get("CRÍTICO", 0))

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🟢 OK", ok)
    k2.metric("🟡 Monitoreo", monitoreo)
    k3.metric("🟠 Programar cambio", programar)
    k4.metric("🔴 Crítico", critico)
else:
    st.info("Sin datos para estado de flota.")


st.divider()
st.subheader("Ranking de desgaste por equipo")

if not ultimos_flot.empty and "condicion_pct" in ultimos_flot.columns:
    ranking = ultimos_flot[["equipo", "condicion_pct"]].copy()
    ranking = ranking.sort_values("condicion_pct", ascending=False)
    ranking = ranking.rename(columns={"condicion_pct": "desgaste_pct"})
    st.bar_chart(ranking.set_index("equipo"))
    st.dataframe(ranking, width="stretch")
else:
    st.info("Sin datos para ranking de desgaste.")


st.divider()
st.subheader("Proyección de cambio")

if not ultimos_flot.empty:
    cols_proj = [c for c in ["equipo", "mm_usada", "estado", "tasa_mm_h", "horas_a_critico", "dias_a_critico"] if c in ultimos_flot.columns]
    proy = ultimos_flot[cols_proj].copy()
    if "horas_a_critico" in proy.columns:
        proy = proy.sort_values("horas_a_critico", na_position="last")
    st.dataframe(proy, width="stretch")
else:
    st.info("Sin datos para proyección.")


st.divider()
st.subheader("Reporte semanal")

df_all = cargar_historial(limit=5000)
if not df_all.empty and "semana_medicion" in df_all.columns:
    semanas_validas = df_all["semana_medicion"].dropna()
    semanas_disponibles = sorted(semanas_validas.astype(int).unique().tolist(), reverse=True)

    if semanas_disponibles:
        semana_sel = st.selectbox("Semana a reportar", semanas_disponibles, index=0)

        equipos_disp = ["TODOS"] + sorted(df_all["equipo"].dropna().astype(str).unique().tolist())
        equipo_sel = st.selectbox("Equipo a reportar", equipos_disp, index=0)

        df_sem = df_all[df_all["semana_medicion"] == semana_sel].copy()
        if equipo_sel != "TODOS":
            df_sem = df_sem[df_sem["equipo"].astype(str) == equipo_sel].copy()

        df_reporte = df_sem.copy()
        df_reporte["criticidad"] = df_reporte["condicion_pct"]

        columnas_reporte = ["equipo", "semana_medicion", "usuario", "horometro", "criticidad", "estado"]
        columnas_reporte = [c for c in columnas_reporte if c in df_reporte.columns]
        df_reporte = df_reporte[columnas_reporte]

        st.download_button(
            "Descargar reporte semanal Excel",
            data=generar_excel_bytes(df_reporte),
            file_name=f"reporte_semana_{semana_sel}_{equipo_sel}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        resumen_mail = generar_resumen_mail(ultimos_estados_por_equipo(df_sem))
        st.text_area("Resumen para correo semanal", value=resumen_mail, height=150)
    else:
        st.info("No hay semanas válidas para reportar.")
else:
    st.info("Aún no hay datos suficientes para reporte semanal.")


st.divider()
st.subheader("Administración de datos")

if admin_ok:
    with open(DB_PATH, "rb") as f:
        db_bytes = f.read()

    st.download_button(
        "Descargar base de datos SQLite",
        data=db_bytes,
        file_name="mediciones.db",
        mime="application/octet-stream"
    )

    st.markdown("### Eliminar registros de prueba")
    if st.button("Eliminar registros de prueba"):
        borradas_prueba = eliminar_registros_prueba()
        st.success(f"Se eliminaron {borradas_prueba} registros de prueba.")
        st.rerun()
else:
    st.info("La descarga de base y eliminación de mediciones quedan solo para administrador.")

st.caption(
    "Nota: el envío automático de correo todos los miércoles requiere Power Automate o un programador externo."
)