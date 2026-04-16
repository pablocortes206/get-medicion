import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

st.set_page_config(page_title="GET Wear Monitor", layout="wide")

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
st.write("URL usada:", st.secrets["SUPABASE_URL"])

st.title("GET Wear Monitor 🚜")

# ---------- helpers ----------
def calcular_mm_usada(mm_izq: float, mm_der: float) -> float:
    return min(mm_izq, mm_der)

def calcular_desgaste_pct(equipo: str, mm_usada: float) -> float:
    if equipo in ["301", "302", "303"]:
        mm_nuevo = 302.0
        mm_critico = 145.0
    else:
        mm_nuevo = 170.0
        mm_critico = 82.0

    if mm_usada >= mm_nuevo:
        return 0.0
    if mm_usada <= mm_critico:
        return 100.0

    desgaste = ((mm_nuevo - mm_usada) / (mm_nuevo - mm_critico)) * 100
    return round(desgaste, 1)

def clasificar_estado(desgaste_pct: float) -> str:
    if desgaste_pct >= 95:
        return "CRÍTICO"
    if desgaste_pct >= 75:
        return "ALTO"
    if desgaste_pct >= 45:
        return "MEDIO"
    return "OK"

def guardar_medicion(fecha_medicion, equipo, horometro, mm_izq, mm_der, usuario):
    mm_usada = calcular_mm_usada(mm_izq, mm_der)
    desgaste_pct = calcular_desgaste_pct(equipo, mm_usada)
    estado = clasificar_estado(desgaste_pct)

    payload = {
        "fecha": str(fecha_medicion),
        "equipo": str(equipo),
        "horometro": float(horometro),
        "mm_izq": float(mm_izq),
        "mm_der": float(mm_der),
        "mm_usada": float(mm_usada),
        "condicion_pct": float(desgaste_pct),
        "estado": estado,
        "usuario": usuario.strip() if usuario else None,
        "componente": "Cuchilla",
        "es_cambio": False,
    }

    return supabase.table("mediciones").insert(payload).execute()

def cargar_historial():
    st.write("Probando conexión a:", st.secrets["SUPABASE_URL"])
    resp = (
        supabase
        .table("mediciones")
        .select("*")
        .limit(5)
        .execute()
    )
    data = resp.data if resp.data else []
    return pd.DataFrame(data)

# ---------- formulario ----------
st.subheader("Ingreso de medición")

equipo = st.selectbox(
    "Equipo",
    ["101", "102", "103", "104", "105", "106", "108", "201", "202", "203", "204", "205", "301", "302", "303"]
)

fecha_medicion = st.date_input("Fecha de medición", value=date.today())
horometro = st.number_input("Horómetro", min_value=0.0, step=1.0)
mm_izq = st.number_input("Medición IZQ (mm)", min_value=0.0, step=0.1)
mm_der = st.number_input("Medición DER (mm)", min_value=0.0, step=0.1)
usuario = st.text_input("Usuario")

if st.button("Guardar medición"):
    errores = []
    if horometro <= 0:
        errores.append("Debes ingresar un horómetro válido.")
    if mm_izq <= 0 or mm_der <= 0:
        errores.append("Debes ingresar ambas mediciones en mm.")
    if not usuario.strip():
        errores.append("Debes ingresar el usuario.")

    if errores:
        for e in errores:
            st.error(e)
    else:
        try:
            guardar_medicion(
                fecha_medicion=fecha_medicion,
                equipo=equipo,
                horometro=horometro,
                mm_izq=mm_izq,
                mm_der=mm_der,
                usuario=usuario,
            )
            st.success(f"Medición guardada para equipo {equipo}")
        except Exception as e:
            st.error(f"Error guardando en Supabase: {e}")

# ---------- preview ----------
st.divider()
st.subheader("Vista previa cálculo")

mm_usada_preview = calcular_mm_usada(mm_izq, mm_der)
desgaste_preview = calcular_desgaste_pct(equipo, mm_usada_preview)
estado_preview = clasificar_estado(desgaste_preview)

c1, c2, c3 = st.columns(3)
c1.metric("mm usada", f"{mm_usada_preview:.1f}")
c2.metric("desgaste %", f"{desgaste_preview:.1f}%")
c3.metric("estado", estado_preview)

# ---------- historial ----------
st.divider()
st.subheader("Historial")

try:
    df = cargar_historial()
    if not df.empty:
        columnas = [c for c in ["fecha", "equipo", "horometro", "mm_izq", "mm_der", "mm_usada", "condicion_pct", "estado", "usuario"] if c in df.columns]
        st.dataframe(df[columnas], use_container_width=True)
    else:
        st.info("Aún no hay registros.")
except Exception as e:
    st.warning(f"No se pudo cargar historial: {e}")
