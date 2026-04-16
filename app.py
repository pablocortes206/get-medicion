from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Dict, List, Tuple

import pandas as pd
import streamlit as st
from supabase import create_client, Client


# =========================================================
# CONFIG APP
# =========================================================
st.set_page_config(page_title="GET Wear Monitor", layout="wide")

TECK_GREEN = "#007A3D"
TECK_GREEN_2 = "#00A04A"
TECK_DARK = "#0B0F14"

EQUIPOS = [
    "101", "102", "103", "104", "105", "106", "108",
    "201", "202", "203", "204", "205",
    "301", "302", "303",
]

EQUIPOS_MOTONIVELADORA = {"301", "302", "303"}

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")


# =========================================================
# ESTILO
# =========================================================
def inject_teck_style() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(1200px 800px at 10% 10%, #101826 0%, {TECK_DARK} 55%, #070A0E 100%);
        }}
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="teck-header">
          <div>
            <p style="font-size:52px; font-weight:900; margin:0; line-height:1.05;">
              GET Wear Monitor
            </p>
            <p style="font-size:22px; margin:6px 0 0 0; opacity:.92;">
              Sistema de monitoreo y proyección de desgaste de cuchillas
            </p>
            <p style="font-size:16px; margin:10px 0 0 0; opacity:.82;">
              <b>Creado por:</b> Pablo Cortés Ramos
            </p>
          </div>
          <div class="teck-badge">Teck QB2 · GET Wear Monitor</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SUPABASE
# =========================================================
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)


supabase = get_supabase()


# =========================================================
# REGLAS
# =========================================================
REGLAS: Dict[str, dict] = {
    "MOTONIVELADORA": {
        "puntos": [
            (122, 100), (145, 91), (167, 78), (190, 65),
            (212, 52), (235, 39), (257, 26), (280, 13), (302, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 90, "Cambiar cuchilla / condición inaceptable."),
            ("MEDIO", 65, "Monitorear condición."),
            ("OK", 0, "Operación normal."),
        ],
        "mm_nuevo": 302.0,
        "mm_critico": 145.0,
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
    },
}


@dataclass
class Resultado:
    mm_usada: float
    desgaste_pct: float
    estado: str
    accion: str
    tasa_mm_h: Optional[float]
    horas_a_critico: Optional[float]
    dias_a_critico: Optional[float]


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


def proyectar_a_critico(mm_usada: float, tasa_mm_h: Optional[float], mm_critico: float) -> tuple[Optional[float], Optional[float]]:
    if tasa_mm_h is None or tasa_mm_h <= 0:
        return None, None

    restante_mm = mm_usada - mm_critico
    if restante_mm <= 0:
        return 0.0, 0.0

    horas = restante_mm / tasa_mm_h
    dias = horas / 24
    return round(horas, 1), round(dias, 1)


# =========================================================
# DATOS SUPABASE
# =========================================================
@st.cache_data(ttl=60)
def cargar_historial(limit: int = 500) -> pd.DataFrame:
    resp = (
        supabase
        .table("mediciones")
        .select("*")
        .order("fecha", desc=True)
        .limit(limit)
        .execute()
    )
    return pd.DataFrame(resp.data or [])


@st.cache_data(ttl=60)
def cargar_cambios(limit: int = 500) -> pd.DataFrame:
    resp = (
        supabase
        .table("cambios_cuchilla")
        .select("*")
        .order("fecha", desc=True)
        .limit(limit)
        .execute()
    )
    return pd.DataFrame(resp.data or [])


def obtener_ultimo_cambio_equipo(equipo: str) -> Optional[dict]:
    resp = (
        supabase
        .table("cambios_cuchilla")
        .select("fecha,horometro")
        .eq("equipo", equipo)
        .order("fecha", desc=True)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    return data[0] if data else None


def obtener_ultimas_mediciones_equipo(equipo: str, n: int = 5) -> list[dict]:
    ultimo = obtener_ultimo_cambio_equipo(equipo)

    q = (
        supabase
        .table("mediciones")
        .select("fecha,horometro,mm_usada")
        .eq("equipo", equipo)
        .eq("es_cambio", False)
        .order("fecha", desc=True)
        .limit(n)
    )

    if ultimo:
        q = q.gte("fecha", ultimo["fecha"])

    resp = q.execute()
    return resp.data or []


def calcular_tasa_mm_h_promedio(meds: list[dict]) -> Optional[float]:
    if len(meds) < 2:
        return None

    tasas = []
    for i in range(len(meds) - 1):
        new = meds[i]
        old = meds[i + 1]

        h_new = float(new["horometro"])
        h_old = float(old["horometro"])
        mm_new = float(new["mm_usada"])
        mm_old = float(old["mm_usada"])

        dh = h_new - h_old
        dmm = mm_old - mm_new

        if dh > 0 and dmm > 0:
            tasas.append(dmm / dh)

    if not tasas:
        return None

    return round(sum(tasas) / len(tasas), 4)


def evaluar(equipo: str, horometro: float, mm_izq: float, mm_der: float) -> Resultado:
    mm_usada = min(mm_izq, mm_der)
    regla = regla_por_equipo(equipo)
    cfg = REGLAS[regla]

    desgaste = round(interpolar_pct(mm_usada, cfg["puntos"]), 1)
    estado, accion = clasificar_desgaste(desgaste, cfg["umbrales"])

    historial = obtener_ultimas_mediciones_equipo(equipo, n=5)
    meds = [{"horometro": horometro, "mm_usada": mm_usada}] + historial

    tasa_mm_h = calcular_tasa_mm_h_promedio(meds)
    horas_a_critico, dias_a_critico = proyectar_a_critico(mm_usada, tasa_mm_h, cfg["mm_critico"])

    return Resultado(
        mm_usada=mm_usada,
        desgaste_pct=desgaste,
        estado=estado,
        accion=accion,
        tasa_mm_h=tasa_mm_h,
        horas_a_critico=horas_a_critico,
        dias_a_critico=dias_a_critico,
    )


def guardar_medicion(
    fecha_medicion: date,
    equipo: str,
    horometro: float,
    mm_izq: float,
    mm_der: float,
    usuario: str,
    res: Resultado,
) -> None:
    payload = {
        "fecha": str(fecha_medicion),
        "equipo": equipo,
        "horometro": float(horometro),
        "mm_izq": float(mm_izq),
        "mm_der": float(mm_der),
        "mm_usada": float(res.mm_usada),
        "condicion_pct": float(res.desgaste_pct),
        "estado": res.estado,
        "accion": res.accion,
        "tasa_mm_h": float(res.tasa_mm_h) if res.tasa_mm_h is not None else None,
        "horas_a_critico": float(res.horas_a_critico) if res.horas_a_critico is not None else None,
        "dias_a_critico": float(res.dias_a_critico) if res.dias_a_critico is not None else None,
        "usuario": usuario.strip(),
        "componente": "Cuchilla",
        "es_cambio": False,
        "creado_en": datetime.utcnow().isoformat(),
    }
    supabase.table("mediciones").insert(payload).execute()
    cargar_historial.clear()


def guardar_cambio_cuchilla(
    fecha_cambio: date,
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
) -> None:
    payload_cambio = {
        "fecha": str(fecha_cambio),
        "equipo": equipo,
        "horometro": float(horometro),
        "mm_izq_final": float(mm_izq_final),
        "mm_der_final": float(mm_der_final),
        "fue_virada": fue_virada,
        "motivo": motivo,
        "observaciones": observaciones.strip() if observaciones else None,
        "tecnico_1": tecnico_1.strip(),
        "tecnico_2": tecnico_2.strip() if tecnico_2 else None,
        "usuario": usuario.strip(),
        "creado_en": datetime.utcnow().isoformat(),
    }
    supabase.table("cambios_cuchilla").insert(payload_cambio).execute()

    regla = regla_por_equipo(equipo)
    mm_nuevo = REGLAS[regla]["mm_nuevo"]

    payload_nuevo = {
        "fecha": str(fecha_cambio),
        "equipo": equipo,
        "horometro": float(horometro),
        "mm_izq": mm_nuevo,
        "mm_der": mm_nuevo,
        "mm_usada": mm_nuevo,
        "condicion_pct": 0.0,
        "estado": "OK",
        "accion": "GET nuevo instalado — iniciar monitoreo.",
        "usuario": tecnico_1.strip() if tecnico_1 else usuario.strip(),
        "componente": "Cuchilla NUEVA",
        "es_cambio": True,
        "creado_en": datetime.utcnow().isoformat(),
    }
    supabase.table("mediciones").insert(payload_nuevo).execute()

    cargar_historial.clear()
    cargar_cambios.clear()


def ultimos_estados_por_equipo(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df2 = df.copy()
    df2["fecha_dt"] = pd.to_datetime(df2["fecha"], errors="coerce")
    df2 = df2.sort_values("fecha_dt", ascending=False)
    return df2.drop_duplicates(subset=["equipo"], keep="first")


# =========================================================
# UI
# =========================================================
inject_teck_style()
render_header()

with st.sidebar:
    st.subheader("Administración")
    admin_ok = False
    if ADMIN_PASSWORD:
        pwd = st.text_input("Clave administrador", type="password")
        admin_ok = pwd == ADMIN_PASSWORD
        if admin_ok:
            st.success("Modo administrador activo")

tabs = st.tabs([
    "📏 Ingreso Medición",
    "🔄 Cambio de Cuchilla",
    "📋 Historial",
    "🔧 Registro de Cambios",
    "🚛 Estado Flota",
])

# =========================================================
# TAB 1
# =========================================================
with tabs[0]:
    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.subheader("Ingreso de medición")

        equipo = st.selectbox("Equipo", EQUIPOS)
        fecha_medicion = st.date_input("Fecha de medición", value=date.today())
        usuario = st.text_input("Usuario")

        st.divider()

        horometro = st.number_input("Horómetro", min_value=0.0, step=1.0)
        regla = regla_por_equipo(equipo)
        mm_max = REGLAS[regla]["mm_nuevo"]

        mm_izq = st.number_input("Medición IZQ (mm)", min_value=0.0, value=mm_max, step=0.1)
        mm_der = st.number_input("Medición DER (mm)", min_value=0.0, value=mm_max, step=0.1)

        ultimo_cambio = obtener_ultimo_cambio_equipo(equipo)
        if ultimo_cambio:
            st.info(f"Último cambio: {ultimo_cambio['fecha']} · Horómetro: {ultimo_cambio['horometro']}")

        if st.button("Guardar medición", type="primary"):
            errores = []
            if not usuario.strip():
                errores.append("Debes ingresar usuario.")
            if horometro <= 0:
                errores.append("Debes ingresar un horómetro válido.")

            mm_min, mm_max_rango = rango_regla(regla)
            if not (mm_min <= mm_izq <= mm_max_rango):
                errores.append(f"Medición IZQ fuera de rango ({mm_min}-{mm_max_rango}).")
            if not (mm_min <= mm_der <= mm_max_rango):
                errores.append(f"Medición DER fuera de rango ({mm_min}-{mm_max_rango}).")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                try:
                    res = evaluar(equipo, horometro, mm_izq, mm_der)
                    guardar_medicion(fecha_medicion, equipo, horometro, mm_izq, mm_der, usuario, res)
                    st.success("Medición guardada correctamente.")
                except Exception as e:
                    st.error(f"Error guardando medición: {e}")

    with c2:
        st.subheader("Vista previa cálculo")
        try:
            res_preview = evaluar(equipo, horometro, mm_izq, mm_der)
            k1, k2, k3 = st.columns(3)
            k1.metric("mm usada", f"{res_preview.mm_usada:.1f}")
            k2.metric("desgaste %", f"{res_preview.desgaste_pct:.1f}%")
            k3.metric("estado", res_preview.estado)

            st.write("**Acción recomendada:**", res_preview.accion)
            if res_preview.tasa_mm_h is not None:
                st.write(f"**Tasa estimada:** {res_preview.tasa_mm_h} mm/h")
            if res_preview.horas_a_critico is not None:
                st.write(f"**Proyección a crítico:** {res_preview.horas_a_critico} h / {res_preview.dias_a_critico} días")
        except Exception as e:
            st.warning(f"No se pudo calcular vista previa: {e}")


# =========================================================
# TAB 2
# =========================================================
with tabs[1]:
    st.subheader("Cambio de cuchilla")

    c1, c2 = st.columns(2)

    with c1:
        eq_cambio = st.selectbox("Equipo", EQUIPOS, key="eq_cambio")
        fecha_cambio = st.date_input("Fecha de cambio", value=date.today(), key="fecha_cambio")
        hr_cambio = st.number_input("Horómetro cambio", min_value=0.0, step=1.0, key="hr_cambio")

        regla_cambio = regla_por_equipo(eq_cambio)
        mm_critico = REGLAS[regla_cambio]["mm_critico"]

        mm_izq_final = st.number_input("IZQ final (mm)", min_value=0.0, value=mm_critico, step=0.1, key="mi_cambio")
        mm_der_final = st.number_input("DER final (mm)", min_value=0.0, value=mm_critico, step=0.1, key="md_cambio")
        fue_virada = st.radio("¿Fue virada?", ["NO", "SÍ"], horizontal=True)

    with c2:
        motivo = st.selectbox(
            "Motivo",
            [
                "Desgaste normal",
                "Preventivo",
                "Daño / impacto",
                "Campaña de mantenimiento",
                "Otro",
            ],
        )
        tecnico_1 = st.text_input("Técnico 1")
        tecnico_2 = st.text_input("Técnico 2")
        observaciones = st.text_area("Observaciones")
        usuario_cambio =
