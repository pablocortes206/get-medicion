from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Dict, List, Tuple
import io

import pandas as pd
import streamlit as st
from supabase import create_client, Client

# =========================================================
# CONFIG
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


# =========================================================
# ESTILO
# =========================================================
def inject_style():
    st.markdown(f"""
    <style>
    .stApp {{
        background: radial-gradient(1200px 800px at 10% 10%, #101826 0%, {TECK_DARK} 55%, #070A0E 100%);
    }}
    .block-container {{ padding-top:1rem !important; padding-bottom:2rem !important; }}
    .teck-header {{
        display:flex; align-items:center; justify-content:space-between; gap:1rem;
        padding:16px 20px; border-radius:16px;
        background:linear-gradient(90deg,rgba(0,122,61,.28) 0%,rgba(0,160,74,.12) 45%,rgba(255,255,255,.03) 100%);
        border:1px solid rgba(0,160,74,.35); box-shadow:0 12px 30px rgba(0,0,0,.35); margin-bottom:18px;
    }}
    .teck-badge {{
        padding:8px 12px; border-radius:999px; font-size:.85rem; font-weight:800; color:white;
        background:linear-gradient(180deg,{TECK_GREEN_2} 0%,{TECK_GREEN} 100%);
        border:1px solid rgba(255,255,255,.18); white-space:nowrap;
    }}
    div.stButton > button {{ border-radius:12px !important; font-weight:800 !important; }}
    div.stButton > button[kind="primary"] {{
        background:linear-gradient(180deg,{TECK_GREEN_2} 0%,{TECK_GREEN} 100%) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="teck-header">
      <div>
        <p style="font-size:52px;font-weight:900;margin:0;line-height:1.05;">GET Wear Monitor</p>
        <p style="font-size:22px;margin:6px 0 0 0;opacity:.92;">Sistema de monitoreo y proyección de desgaste de cuchillas</p>
        <p style="font-size:15px;margin:8px 0 0 0;opacity:.75;"><b>Creado por:</b> Pablo Cortés Ramos · Ingeniero de Mantenimiento / Confiabilidad</p>
      </div>
      <div class="teck-badge">Teck QB2 · GET Wear Monitor</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SUPABASE
# =========================================================
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)


def sb() -> Client:
    return get_supabase()


# =========================================================
# LÓGICA
# =========================================================
def regla_por_equipo(equipo: str) -> str:
    return "MOTONIVELADORA" if equipo in EQUIPOS_MOTONIVELADORA else "DOZER_854_D10_D11"


def rango_regla(regla: str) -> tuple[float, float]:
    xs = [p[0] for p in REGLAS[regla]["puntos"]]
    return min(xs), max(xs)


def interpolar_pct(mm: float, puntos: List[Tuple[float, float]]) -> float:
    puntos = sorted(puntos, key=lambda x: x[0])
    if mm <= puntos[0][0]: return float(puntos[0][1])
    if mm >= puntos[-1][0]: return float(puntos[-1][1])
    for (x1, y1), (x2, y2) in zip(puntos[:-1], puntos[1:]):
        if x1 <= mm <= x2:
            return float(y1 + (mm - x1) / (x2 - x1) * (y2 - y1))
    return float(puntos[-1][1])


def clasificar(pct: float, umbrales) -> tuple[str, str]:
    for estado, limite, accion in umbrales:
        if pct >= limite:
            return estado, accion
    return "OK", "Operación normal."


def calcular_tasa(meds: list[dict]) -> Optional[float]:
    if len(meds) < 2: return None
    tasas = []
    for i in range(len(meds) - 1):
        dh = float(meds[i]["horometro"]) - float(meds[i+1]["horometro"])
        dmm = float(meds[i+1]["mm_usada"]) - float(meds[i]["mm_usada"])
        if dh > 0 and dmm > 0:
            tasas.append(dmm / dh)
    return round(sum(tasas)/len(tasas), 4) if tasas else None


def proyectar(mm_usada: float, tasa: Optional[float], mm_critico: float) -> tuple[Optional[float], Optional[float]]:
    if not tasa or tasa <= 0: return None, None
    restante = mm_usada - mm_critico
    if restante <= 0: return 0.0, 0.0
    h = restante / tasa
    return round(h, 1), round(h / 24, 1)


# =========================================================
# DB QUERIES
# =========================================================
@st.cache_data(ttl=60)
def cargar_historial(limit: int = 500) -> pd.DataFrame:
    resp = sb().table("mediciones").select("*").order("fecha", desc=True).limit(limit).execute()
    return pd.DataFrame(resp.data or [])


@st.cache_data(ttl=60)
def cargar_cambios(limit: int = 200) -> pd.DataFrame:
    resp = sb().table("cambios_cuchilla").select("*").order("fecha", desc=True).limit(limit).execute()
    return pd.DataFrame(resp.data or [])


def ultimo_cambio_equipo(equipo: str) -> Optional[dict]:
    resp = sb().table("cambios_cuchilla").select("fecha,horometro").eq("equipo", equipo).order("fecha", desc=True).limit(1).execute()
    data = resp.data or []
    return data[0] if data else None


def ultimas_meds_equipo(equipo: str, n: int = 5) -> list[dict]:
    uc = ultimo_cambio_equipo(equipo)
    q = sb().table("mediciones").select("fecha,horometro,mm_usada").eq("equipo", equipo).eq("es_cambio", False).order("fecha", desc=True).limit(n)
    if uc:
        q = q.gte("fecha", uc["fecha"])
    return q.execute().data or []


def evaluar(equipo: str, horometro: float, mm_izq: float, mm_der: float) -> dict:
    mm_usada = min(mm_izq, mm_der)
    regla = regla_por_equipo(equipo)
    cfg = REGLAS[regla]
    pct = round(interpolar_pct(mm_usada, cfg["puntos"]), 1)
    estado, accion = clasificar(pct, cfg["umbrales"])
    hist = ultimas_meds_equipo(equipo, 5)
    meds = [{"horometro": horometro, "mm_usada": mm_usada}] + hist
    tasa = calcular_tasa(meds)
    h_critico, d_critico = proyectar(mm_usada, tasa, cfg["mm_critico"])
    return dict(mm_usada=mm_usada, pct=pct, estado=estado, accion=accion,
                tasa=tasa, h_critico=h_critico, d_critico=d_critico, regla=regla)


def guardar_medicion(fecha, equipo, horometro, mm_izq, mm_der, usuario, r):
    sb().table("mediciones").insert({
        "fecha": str(fecha), "equipo": equipo,
        "horometro": float(horometro), "mm_izq": float(mm_izq), "mm_der": float(mm_der),
        "mm_usada": float(r["mm_usada"]), "condicion_pct": float(r["pct"]),
        "estado": r["estado"], "accion": r["accion"],
        "tasa_mm_h": float(r["tasa"]) if r["tasa"] else None,
        "horas_a_critico": float(r["h_critico"]) if r["h_critico"] is not None else None,
        "dias_a_critico": float(r["d_critico"]) if r["d_critico"] is not None else None,
        "usuario": usuario.strip(), "componente": "Cuchilla", "es_cambio": False,
        "creado_en": datetime.utcnow().isoformat(),
    }).execute()
    cargar_historial.clear()


def guardar_cambio(fecha, equipo, horometro, mm_izq_f, mm_der_f, fue_virada, motivo, obs, tec1, tec2, usuario):
    sb().table("cambios_cuchilla").insert({
        "fecha": str(fecha), "equipo": equipo, "horometro": float(horometro),
        "mm_izq_final": float(mm_izq_f), "mm_der_final": float(mm_der_f),
        "fue_virada": fue_virada, "motivo": motivo,
        "observaciones": obs.strip() if obs else None,
        "tecnico_1": tec1.strip(), "tecnico_2": tec2.strip() if tec2 else None,
        "usuario": usuario.strip(), "creado_en": datetime.utcnow().isoformat(),
    }).execute()
    regla = regla_por_equipo(equipo)
    mm_nuevo = REGLAS[regla]["mm_nuevo"]
    sb().table("mediciones").insert({
        "fecha": str(fecha), "equipo": equipo, "horometro": float(horometro),
        "mm_izq": mm_nuevo, "mm_der": mm_nuevo, "mm_usada": mm_nuevo,
        "condicion_pct": 0.0, "estado": "OK", "accion": "GET nuevo instalado.",
        "usuario": tec1.strip() if tec1 else usuario.strip(),
        "componente": "Cuchilla NUEVA", "es_cambio": True,
        "creado_en": datetime.utcnow().isoformat(),
    }).execute()
    cargar_historial.clear()
    cargar_cambios.clear()


def ultimos_por_equipo(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df2 = df.copy()
    df2["fecha_dt"] = pd.to_datetime(df2["fecha"], errors="coerce")
    return df2.sort_values("fecha_dt", ascending=False).drop_duplicates("equipo", keep="first")


def excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    return buf.getvalue()


# =========================================================
# APP
# =========================================================
inject_style()
render_header()

with st.sidebar:
    st.subheader("Administración")
    admin_ok = False
    if ADMIN_PASSWORD:
        pwd = st.text_input("Clave administrador", type="password")
        admin_ok = pwd == ADMIN_PASSWORD
        if admin_ok:
            st.success("Modo administrador activo")
    else:
        st.info("Sin clave configurada.")

tabs = st.tabs([
    "📏 Ingreso Medición",
    "🔄 Cambio de Cuchilla",
    "📋 Historial",
    "🔧 Registro de Cambios",
    "🚛 Estado Flota",
    "📊 Reporte",
])

# ─────────────────────────────────────────────
# TAB 1: INGRESO MEDICIÓN
# ─────────────────────────────────────────────
with tabs[0]:
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.subheader("Ingreso de medición")
        equipo = st.selectbox("Equipo", EQUIPOS, key="eq_m")
        fecha_m = st.date_input("Fecha", value=date.today(), key="f_m")
        usuario_m = st.text_input("Técnico", key="u_m")
        st.divider()
        regla = regla_por_equipo(equipo)
        mm_max = REGLAS[regla]["mm_nuevo"]
        horometro_m = st.number_input("Horómetro", min_value=0.0, step=1.0, key="h_m")
        mm_izq_m = st.number_input("Medición IZQ (mm)", min_value=0.0, value=mm_max, step=0.1, key="mi_m")
        mm_der_m = st.number_input("Medición DER (mm)", min_value=0.0, value=mm_max, step=0.1, key="md_m")
        st.caption("Se usa el valor MENOR (más crítico) para evaluar.")

        uc = ultimo_cambio_equipo(equipo)
        if uc:
            st.info(f"📌 Último cambio: {uc['fecha']} · Horómetro: {uc['horometro']:,.0f} hrs")

        if st.button("Guardar medición", type="primary", key="btn_m"):
            errores = []
            if not usuario_m.strip(): errores.append("Ingresa el nombre del técnico.")
            if horometro_m <= 0: errores.append("Ingresa un horómetro válido.")
            mn, mx = rango_regla(regla)
            if not (mn <= mm_izq_m <= mx): errores.append(f"IZQ fuera de rango ({mn}-{mx} mm).")
            if not (mn <= mm_der_m <= mx): errores.append(f"DER fuera de rango ({mn}-{mx} mm).")
            if errores:
                for e in errores: st.error(e)
            else:
                try:
                    r = evaluar(equipo, horometro_m, mm_izq_m, mm_der_m)
                    guardar_medicion(fecha_m, equipo, horometro_m, mm_izq_m, mm_der_m, usuario_m, r)
                    st.success("✅ Medición guardada.")
                    color = {"OK":"🟢","MEDIO":"🟡","ALTO":"🟠","CRÍTICO":"🔴"}.get(r["estado"],"⚪")
                    st.metric("Estado", f"{color} {r['estado']}")
                    st.metric("Desgaste %", f"{r['pct']:.1f}%")
                    st.metric("mm usada", f"{r['mm_usada']:.1f}")
                    if r["tasa"]: st.info(f"Tasa: {r['tasa']} mm/h")
                    if r["h_critico"] is not None:
                        st.warning(f"⏱ Proyección a crítico: ~{r['h_critico']} h / ~{r['d_critico']} días")
                except Exception as e:
                    st.error(f"Error: {e}")

    with c2:
        st.subheader("Historial del equipo")
        df_eq = cargar_historial()
        if not df_eq.empty:
            df_show = df_eq[df_eq["equipo"] == equipo].head(15)
            if not df_show.empty:
                cols = [c for c in ["fecha","horometro","mm_usada","condicion_pct","estado","usuario"] if c in df_show.columns]
                st.dataframe(df_show[cols], use_container_width=True)
            else:
                st.info(f"Sin mediciones para equipo {equipo}.")


# ─────────────────────────────────────────────
# TAB 2: CAMBIO DE CUCHILLA
# ─────────────────────────────────────────────
with tabs[1]:
    st.subheader("🔄 Registro de Cambio de Cuchilla")
    st.caption("Registra la instalación de un GET nuevo. Reinicia el ciclo de desgaste.")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        eq_c = st.selectbox("Equipo", EQUIPOS, key="eq_c")
        fecha_c = st.date_input("Fecha de cambio", value=date.today(), key="f_c")
        hr_c = st.number_input("Horómetro al cambio", min_value=0.0, step=1.0, key="h_c")
        regla_c = regla_por_equipo(eq_c)
        mm_critico_c = REGLAS[regla_c]["mm_critico"]
        mm_max_c = REGLAS[regla_c]["mm_nuevo"]
        mm_izq_c = st.number_input("IZQ final del GET retirado (mm)", min_value=0.0, max_value=float(mm_max_c), value=float(mm_critico_c), step=0.1, key="mi_c")
        mm_der_c = st.number_input("DER final del GET retirado (mm)", min_value=0.0, max_value=float(mm_max_c), value=float(mm_critico_c), step=0.1, key="md_c")
        virada_c = st.radio("¿Fue virada?", ["NO", "SÍ"], horizontal=True, key="v_c")
        motivo_c = st.selectbox("Motivo", ["Desgaste normal","Preventivo","Daño / impacto","Campaña mantenimiento","Otro"], key="mot_c")

    with c2:
        tec1_c = st.text_input("Técnico 1", key="t1_c")
        tec2_c = st.text_input("Técnico 2 (opcional)", key="t2_c")
        obs_c = st.text_area("Observaciones / OT generadas", height=120, key="obs_c")
        supervisor_c = st.text_input("Registrado por", key="sup_c")
        st.divider()
        st.info(f"Al confirmar: se inicia ciclo nuevo con **{mm_max_c:.0f} mm**")

        if st.button("✅ Confirmar cambio de cuchilla", type="primary", key="btn_c"):
            errores = []
            if hr_c <= 0: errores.append("Horómetro debe ser mayor que 0.")
            if not tec1_c.strip(): errores.append("Ingresa al menos el Técnico 1.")
            if not supervisor_c.strip(): errores.append("Ingresa quién registra el cambio.")
            if errores:
                for e in errores: st.error(e)
            else:
                try:
                    guardar_cambio(fecha_c, eq_c, hr_c, mm_izq_c, mm_der_c,
                                   virada_c=="SÍ", motivo_c, obs_c, tec1_c, tec2_c, supervisor_c)
                    st.success(f"🔄 Cambio registrado para Equipo **{eq_c}** · Horómetro: **{hr_c:,.0f} hrs**")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")


# ─────────────────────────────────────────────
# TAB 3: HISTORIAL
# ─────────────────────────────────────────────
with tabs[2]:
    st.subheader("📋 Historial completo")
    df_h = cargar_historial()
    if not df_h.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            eq_fil = st.multiselect("Equipo", sorted(df_h["equipo"].unique()), key="fil_eq")
        with col_f2:
            est_fil = st.multiselect("Estado", sorted(df_h["estado"].dropna().unique()), key="fil_est")
        df_show_h = df_h.copy()
        if eq_fil: df_show_h = df_show_h[df_show_h["equipo"].isin(eq_fil)]
        if est_fil: df_show_h = df_show_h[df_show_h["estado"].isin(est_fil)]
        cols_h = [c for c in ["fecha","equipo","horometro","mm_izq","mm_der","mm_usada","condicion_pct","estado","usuario"] if c in df_show_h.columns]
        st.dataframe(df_show_h[cols_h], use_container_width=True)
        st.download_button("⬇️ Descargar Excel", data=excel_bytes(df_show_h[cols_h]), file_name="historial.xlsx")
    else:
        st.info("Sin mediciones aún.")


# ─────────────────────────────────────────────
# TAB 4: REGISTRO DE CAMBIOS
# ─────────────────────────────────────────────
with tabs[3]:
    st.subheader("🔧 Historial de cambios de cuchilla")
    df_cam = cargar_cambios()
    if not df_cam.empty:
        df_cam["fue_virada"] = df_cam["fue_virada"].map({True:"SÍ", False:"NO", 1:"SÍ", 0:"NO"})
        cols_c = [c for c in ["fecha","equipo","horometro","mm_izq_final","mm_der_final","fue_virada","motivo","tecnico_1","tecnico_2","observaciones","usuario"] if c in df_cam.columns]
        st.dataframe(df_cam[cols_c], use_container_width=True)
        st.download_button("⬇️ Descargar Excel", data=excel_bytes(df_cam[cols_c]), file_name="cambios_cuchilla.xlsx")

        st.divider()
        st.markdown("#### Resumen por equipo")
        resumen = df_cam.groupby("equipo").agg(total_cambios=("id","count"), ultimo_cambio=("fecha","max")).reset_index()
        st.dataframe(resumen, use_container_width=True)
    else:
        st.info("Sin cambios registrados aún.")


# ─────────────────────────────────────────────
# TAB 5: ESTADO FLOTA
# ─────────────────────────────────────────────
with tabs[4]:
    st.subheader("🚛 Estado de flota")
    df_flota = cargar_historial(5000)
    ultimos = ultimos_por_equipo(df_flota)

    if not ultimos.empty:
        ec = ultimos["estado"].value_counts()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🟢 OK", int(ec.get("OK", 0)))
        k2.metric("🟡 Monitoreo", int(ec.get("MEDIO", 0)))
        k3.metric("🟠 Programar cambio", int(ec.get("ALTO", 0)))
        k4.metric("🔴 Crítico", int(ec.get("CRÍTICO", 0)))

        st.divider()
        st.subheader("Desgaste por equipo (%)")
        if "condicion_pct" in ultimos.columns:
            ranking = ultimos[["equipo","condicion_pct"]].sort_values("condicion_pct", ascending=False).set_index("equipo")
            st.bar_chart(ranking)

        st.divider()
        st.subheader("Proyección de cambios")
        cols_p = [c for c in ["equipo","mm_usada","condicion_pct","estado","tasa_mm_h","horas_a_critico","dias_a_critico"] if c in ultimos.columns]
        proy = ultimos[cols_p].sort_values("horas_a_critico", na_position="last") if "horas_a_critico" in cols_p else ultimos[cols_p]
        st.dataframe(proy, use_container_width=True)
    else:
        st.info("Sin datos de flota aún.")


# ─────────────────────────────────────────────
# TAB 6: REPORTE
# ─────────────────────────────────────────────
with tabs[5]:
    st.subheader("📊 Reporte")
    df_rep = cargar_historial(5000)
    if not df_rep.empty:
        eq_rep = st.selectbox("Equipo", ["TODOS"] + sorted(df_rep["equipo"].unique()), key="eq_rep")
        df_r = df_rep if eq_rep == "TODOS" else df_rep[df_rep["equipo"] == eq_rep]
        cols_r = [c for c in ["fecha","equipo","horometro","mm_usada","condicion_pct","estado","usuario"] if c in df_r.columns]
        st.dataframe(df_r[cols_r].head(100), use_container_width=True)
        st.download_button("⬇️ Descargar reporte Excel", data=excel_bytes(df_r[cols_r]), file_name=f"reporte_{eq_rep}.xlsx")
    else:
        st.info("Sin datos.")

    if admin_ok:
        st.divider()
        st.subheader("Administración")
        if st.button("🗑️ Limpiar caché"):
            cargar_historial.clear()
            cargar_cambios.clear()
            st.success("Caché limpiado.")
