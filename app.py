from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Tuple
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import pandas as pd
import streamlit as st
from supabase import create_client, Client

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="GET Wear Monitor", layout="wide")

TECK_GREEN   = "#007A3D"
TECK_GREEN_2 = "#00A04A"
TECK_DARK    = "#0B0F14"

EQUIPOS = [
    "101","102","103","104","105","106","108",
    "201","202","203","204","205",
    "301","302","303",
]
EQUIPOS_MOTONIVELADORA = {"301","302","303"}

# Mapeo código Excel → ID interno
CODIGO_A_ID = {
    "0174-DZ-101":"101","0174-DZ-102":"102","0174-DZ-103":"103",
    "0174-DZ-104":"104","0174-DZ-105":"105","0174-DZ-106":"106",
    "0174-DZ-108":"108",
    "0174-WD-201":"201","0174-WD-202":"202","0174-WD-203":"203",
    "0174-WD-204":"204","0174-WD-205":"205",
    "0174-GR-301":"301","0174-GR-302":"302","0174-GR-303":"303",
}

REGLAS: Dict[str, dict] = {
    "MOTONIVELADORA": {
        "puntos": [(122,100),(145,91),(167,78),(190,65),(212,52),(235,39),(257,26),(280,13),(302,0)],
        "umbrales": [("CRÍTICO",90,"Cambiar cuchilla."),("MEDIO",65,"Monitorear."),("OK",0,"Operación normal.")],
        "mm_nuevo": 302.0, "mm_critico": 145.0,
    },
    "DOZER_854_D10_D11": {
        "puntos": [(75,100),(82,95),(83,90),(100,75),(140,45),(170,0)],
        "umbrales": [("CRÍTICO",95,"Detención inmediata."),("ALTO",75,"Programar cambio."),("MEDIO",45,"Monitorear."),("OK",0,"Operación normal.")],
        "mm_nuevo": 170.0, "mm_critico": 82.0,
    },
}

COLOR_ESTADO = {"OK":"🟢","MEDIO":"🟡","ALTO":"🟠","CRÍTICO":"🔴"}
BG_ESTADO    = {"OK":"#1a3d1a","MEDIO":"#3d3000","ALTO":"#3d1a00","CRÍTICO":"#3d0000"}


# =========================================================
# ESTILO
# =========================================================
def inject_style():
    st.markdown(f"""
    <style>
    .stApp {{background:radial-gradient(1200px 800px at 10% 10%,#101826 0%,{TECK_DARK} 55%,#070A0E 100%);}}
    .block-container{{padding-top:1rem !important;padding-bottom:2rem !important;}}
    .teck-header{{display:flex;align-items:center;justify-content:space-between;gap:1rem;
        padding:16px 20px;border-radius:16px;
        background:linear-gradient(90deg,rgba(0,122,61,.28) 0%,rgba(0,160,74,.12) 45%,rgba(255,255,255,.03) 100%);
        border:1px solid rgba(0,160,74,.35);box-shadow:0 12px 30px rgba(0,0,0,.35);margin-bottom:18px;}}
    .teck-badge{{padding:8px 12px;border-radius:999px;font-size:.85rem;font-weight:800;color:white;
        background:linear-gradient(180deg,{TECK_GREEN_2} 0%,{TECK_GREEN} 100%);
        border:1px solid rgba(255,255,255,.18);white-space:nowrap;}}
    div.stButton>button{{border-radius:12px !important;font-weight:800 !important;}}
    div.stButton>button[kind="primary"]{{background:linear-gradient(180deg,{TECK_GREEN_2} 0%,{TECK_GREEN} 100%) !important;}}
    .equipo-card{{padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,.1);margin-bottom:8px;}}
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
    return create_client(st.secrets["SUPABASE_URL"].strip(), st.secrets["SUPABASE_KEY"].strip())

def sb() -> Client:
    return get_supabase()


# =========================================================
# LÓGICA DESGASTE
# =========================================================
def regla_por_equipo(eq: str) -> str:
    return "MOTONIVELADORA" if eq in EQUIPOS_MOTONIVELADORA else "DOZER_854_D10_D11"

def rango_regla(regla: str) -> tuple[float,float]:
    xs = [p[0] for p in REGLAS[regla]["puntos"]]
    return min(xs), max(xs)

def interpolar_pct(mm: float, puntos) -> float:
    puntos = sorted(puntos, key=lambda x: x[0])
    if mm <= puntos[0][0]: return float(puntos[0][1])
    if mm >= puntos[-1][0]: return float(puntos[-1][1])
    for (x1,y1),(x2,y2) in zip(puntos[:-1],puntos[1:]):
        if x1 <= mm <= x2:
            return float(y1 + (mm-x1)/(x2-x1)*(y2-y1))
    return float(puntos[-1][1])

def clasificar(pct, umbrales):
    for estado,limite,accion in umbrales:
        if pct >= limite: return estado, accion
    return "OK","Operación normal."

def calcular_tasa_meds(meds: list[dict]) -> Optional[float]:
    """Tasa desde mediciones reales (mm/h)."""
    if len(meds) < 2: return None
    tasas = []
    for i in range(len(meds)-1):
        dh  = float(meds[i]["horometro"]) - float(meds[i+1]["horometro"])
        dmm = float(meds[i+1]["mm_usada"]) - float(meds[i]["mm_usada"])
        if dh > 0 and dmm > 0: tasas.append(dmm/dh)
    return round(sum(tasas)/len(tasas),4) if tasas else None

def proyectar(mm_usada: float, tasa: Optional[float], mm_critico: float):
    if not tasa or tasa <= 0: return None, None
    r = mm_usada - mm_critico
    if r <= 0: return 0.0, 0.0
    h = r / tasa
    return round(h,1), round(h/24,1)


# =========================================================
# LECTURA EXCEL HORÓMETROS
# =========================================================
def leer_excel_horometros(archivo) -> pd.DataFrame:
    """
    Lee la hoja HOROMETRO del Excel de control.
    Columnas esperadas: B=codigo, D=fecha, E=horometro, F=prom_7d, G=prom_30d, H=prom_hist
    Equipos GET en filas 29-43.
    """
    from openpyxl import load_workbook
    wb = load_workbook(archivo, read_only=True, data_only=True)
    ws = wb["HOROMETRO"]

    registros = []
    for row in ws.iter_rows(min_row=29, max_row=43, min_col=2, max_col=8, values_only=True):
        codigo = row[0]  # Col B
        if not codigo or not isinstance(codigo, str): continue
        codigo = codigo.strip()
        if codigo not in CODIGO_A_ID: continue

        equipo_id = CODIGO_A_ID[codigo]
        fecha_act = row[2]  # Col D
        if hasattr(fecha_act, 'date'):
            fecha_act = fecha_act.date()
        elif isinstance(fecha_act, str):
            try: fecha_act = datetime.strptime(fecha_act, "%Y-%m-%d").date()
            except: fecha_act = date.today()
        else:
            fecha_act = date.today()

        horometro   = float(row[3]) if row[3] is not None else None  # Col E
        prom_7d     = float(row[4]) if row[4] is not None else None  # Col F
        prom_30d    = float(row[5]) if row[5] is not None else None  # Col G
        prom_hist   = float(row[6]) if row[6] is not None else None  # Col H

        if horometro is None: continue

        registros.append({
            "codigo_excel": codigo,
            "equipo": equipo_id,
            "fecha": str(fecha_act),
            "horometro_actual": horometro,
            "promedio_7d": prom_7d,
            "promedio_30d": prom_30d,
            "promedio_historico": prom_hist,
        })

    wb.close()
    return pd.DataFrame(registros)


def guardar_horometros(df: pd.DataFrame) -> int:
    """Upsert en tabla horometros. Retorna cantidad procesada."""
    if df.empty: return 0
    count = 0
    for _, row in df.iterrows():
        payload = {
            "fecha": row["fecha"],
            "equipo": row["equipo"],
            "horometro_actual": row["horometro_actual"],
            "promedio_7d": row["promedio_7d"],
            "promedio_30d": row["promedio_30d"],
            "promedio_historico": row["promedio_historico"],
            "creado_en": datetime.utcnow().isoformat(),
        }
        sb().table("horometros").insert(payload).execute()
        count += 1
    cargar_horometros_db.clear()
    return count


@st.cache_data(ttl=300)
def cargar_horometros_db() -> pd.DataFrame:
    """Carga el último horómetro por equipo desde Supabase."""
    try:
        resp = sb().table("horometros").select("*").order("fecha", desc=True).limit(500).execute()
        df = pd.DataFrame(resp.data or [])
        if df.empty: return df
        df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
        return df.sort_values("fecha_dt", ascending=False).drop_duplicates("equipo", keep="first")
    except Exception:
        return pd.DataFrame()


def tasa_por_horometro(equipo: str) -> Optional[float]:
    """
    Calcula tasa mm/h usando:
    1. Mediciones reales (prioritario)
    2. Si no hay suficientes, usa mm_usada / horas promedio del Excel
    """
    return None  # se calcula en evaluar()


def evaluar(eq: str, horometro: float, mm_izq: float, mm_der: float) -> dict:
    mm_usada = min(mm_izq, mm_der)
    regla = regla_por_equipo(eq)
    cfg = REGLAS[regla]
    pct = round(interpolar_pct(mm_usada, cfg["puntos"]), 1)
    estado, accion = clasificar(pct, cfg["umbrales"])

    # Mediciones reales del ciclo actual
    hist = ultimas_meds_equipo(eq, 5)
    meds = [{"horometro": horometro, "mm_usada": mm_usada}] + hist
    tasa = calcular_tasa_meds(meds)

    # Si no hay tasa desde mediciones, usar promedio de horómetros Excel
    if tasa is None:
        df_horo = cargar_horometros_db()
        if not df_horo.empty:
            row_h = df_horo[df_horo["equipo"] == eq]
            if not row_h.empty:
                prom = row_h.iloc[0].get("promedio_30d") or row_h.iloc[0].get("promedio_historico")
                # tasa estimada = desgaste_desde_nuevo / horas_acumuladas
                # Usamos promedio h/día para proyectar directamente
                if prom and prom > 0:
                    # Guardamos el promedio para la proyección
                    h_dia = float(prom)
                    h_c, d_c = proyectar_con_horas_dia(mm_usada, h_dia, cfg["mm_critico"], horometro, eq)
                    return dict(mm_usada=mm_usada, pct=pct, estado=estado, accion=accion,
                                tasa=None, h_critico=h_c, d_critico=d_c, regla=regla,
                                fuente_tasa="Excel horómetros")

    h_c, d_c = proyectar(mm_usada, tasa, cfg["mm_critico"])
    return dict(mm_usada=mm_usada, pct=pct, estado=estado, accion=accion,
                tasa=tasa, h_critico=h_c, d_critico=d_c, regla=regla,
                fuente_tasa="Mediciones reales" if tasa else "Sin datos")


def proyectar_con_horas_dia(mm_usada: float, h_dia: float, mm_critico: float,
                             horometro_actual: float, equipo: str) -> tuple[Optional[float], Optional[float]]:
    """
    Proyecta usando h/día del Excel y la tasa de desgaste histórica del equipo.
    Si no hay tasa histórica, usa tasa promedio de flota.
    """
    # Intentar obtener tasa desde historial completo del equipo
    resp = sb().table("mediciones").select("horometro,mm_usada").eq("equipo", equipo).eq("es_cambio", False).order("fecha", desc=True).limit(10).execute()
    meds_all = resp.data or []
    tasa = calcular_tasa_meds(meds_all)

    if tasa is None or tasa <= 0:
        # Tasa promedio por tipo de equipo
        regla = regla_por_equipo(equipo)
        tasa = 0.013 if regla == "DOZER_854_D10_D11" else 0.028  # mm/h referencial

    restante_mm = mm_usada - mm_critico
    if restante_mm <= 0: return 0.0, 0.0
    horas = restante_mm / tasa
    dias  = horas / h_dia  # días reales considerando uso real del equipo
    return round(horas, 1), round(dias, 1)


# =========================================================
# DB MEDICIONES
# =========================================================
@st.cache_data(ttl=60)
def cargar_historial(limit: int = 500) -> pd.DataFrame:
    try:
        resp = sb().table("mediciones").select("*").order("fecha",desc=True).limit(limit).execute()
        return pd.DataFrame(resp.data or [])
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def cargar_cambios(limit: int = 200) -> pd.DataFrame:
    try:
        resp = sb().table("cambios_cuchilla").select("*").order("fecha",desc=True).limit(limit).execute()
        return pd.DataFrame(resp.data or [])
    except Exception:
        return pd.DataFrame()

def ultimo_cambio_equipo(eq: str) -> Optional[dict]:
    resp = sb().table("cambios_cuchilla").select("fecha,horometro").eq("equipo",eq).order("fecha",desc=True).limit(1).execute()
    data = resp.data or []
    return data[0] if data else None

def ultimas_meds_equipo(eq: str, n: int = 5) -> list[dict]:
    uc = ultimo_cambio_equipo(eq)
    q = sb().table("mediciones").select("fecha,horometro,mm_usada").eq("equipo",eq).eq("es_cambio",False).order("fecha",desc=True).limit(n)
    if uc: q = q.gte("fecha", uc["fecha"])
    return q.execute().data or []

def guardar_medicion(fecha, eq, horometro, mm_izq, mm_der, usuario, r):
    sb().table("mediciones").insert({
        "fecha": str(fecha), "equipo": eq,
        "horometro": float(horometro), "mm_izq": float(mm_izq), "mm_der": float(mm_der),
        "mm_usada": float(r["mm_usada"]), "condicion_pct": float(r["pct"]),
        "estado": r["estado"], "accion": r["accion"],
        "tasa_mm_h": float(r["tasa"]) if r.get("tasa") else None,
        "horas_a_critico": float(r["h_critico"]) if r.get("h_critico") is not None else None,
        "dias_a_critico": float(r["d_critico"]) if r.get("d_critico") is not None else None,
        "usuario": usuario.strip(), "componente": "Cuchilla", "es_cambio": False,
        "creado_en": datetime.utcnow().isoformat(),
    }).execute()
    cargar_historial.clear()

def guardar_cambio(fecha, eq, horometro, mm_izq_f, mm_der_f, fue_virada, motivo, obs, tec1, tec2, usuario):
    sb().table("cambios_cuchilla").insert({
        "fecha": str(fecha), "equipo": eq, "horometro": float(horometro),
        "mm_izq_final": float(mm_izq_f), "mm_der_final": float(mm_der_f),
        "fue_virada": fue_virada, "motivo": motivo,
        "observaciones": obs.strip() if obs else None,
        "tecnico_1": tec1.strip(), "tecnico_2": tec2.strip() if tec2 else None,
        "usuario": usuario.strip(), "creado_en": datetime.utcnow().isoformat(),
    }).execute()
    regla = regla_por_equipo(eq)
    mm_nuevo = REGLAS[regla]["mm_nuevo"]
    sb().table("mediciones").insert({
        "fecha": str(fecha), "equipo": eq, "horometro": float(horometro),
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

def dias_sin_medicion(df: pd.DataFrame) -> pd.DataFrame:
    hoy = date.today()
    rows = []
    for eq in EQUIPOS:
        df_eq = df[df["equipo"] == eq] if not df.empty else pd.DataFrame()
        if df_eq.empty:
            rows.append({"equipo": eq, "ultima_medicion": "—", "dias_sin_medir": None, "estado": "SIN DATOS"})
        else:
            ultima = pd.to_datetime(df_eq["fecha"]).max().date()
            dias = (hoy - ultima).days
            estado_last = df_eq.sort_values("fecha", ascending=False).iloc[0].get("estado","?")
            rows.append({"equipo": eq, "ultima_medicion": str(ultima), "dias_sin_medir": dias, "estado": estado_last})
    return pd.DataFrame(rows)


# =========================================================
# REPORTE CORREO
# =========================================================
def generar_html_reporte(df_estados: pd.DataFrame, df_sin_medir: pd.DataFrame) -> str:
    color_map = {"OK":"#1a5c1a","MEDIO":"#7a6000","ALTO":"#7a3000","CRÍTICO":"#7a0000","SIN DATOS":"#333"}
    texto_map = {"OK":"✅ OK","MEDIO":"🟡 Monitoreo","ALTO":"🟠 Programar cambio","CRÍTICO":"🔴 CRÍTICO","SIN DATOS":"⚫ Sin datos"}

    filas = ""
    if not df_estados.empty:
        for _, r in df_estados.iterrows():
            est = str(r.get("estado",""))
            bg  = color_map.get(est,"#333")
            txt = texto_map.get(est, est)
            mm  = f"{r['mm_usada']:.1f}" if pd.notna(r.get("mm_usada")) else "—"
            pct = f"{r['condicion_pct']:.1f}%" if pd.notna(r.get("condicion_pct")) else "—"
            dias_c = f"{r['dias_a_critico']:.0f} días" if pd.notna(r.get("dias_a_critico")) else "—"
            filas += f"""<tr>
              <td style="padding:8px;font-weight:bold;">{r['equipo']}</td>
              <td style="padding:8px;">{r.get('fecha','—')}</td>
              <td style="padding:8px;">{mm} mm</td>
              <td style="padding:8px;">{pct}</td>
              <td style="padding:8px;background:{bg};border-radius:6px;text-align:center;">{txt}</td>
              <td style="padding:8px;">{dias_c}</td>
            </tr>"""

    sin_medir = df_sin_medir[df_sin_medir["dias_sin_medir"].notna() & (df_sin_medir["dias_sin_medir"] > 7)] if not df_sin_medir.empty else pd.DataFrame()
    filas_sm = "".join(f"<tr><td style='padding:8px;font-weight:bold;'>{r['equipo']}</td><td style='padding:8px;'>{r.get('ultima_medicion','—')}</td><td style='padding:8px;color:#ff9900;font-weight:bold;'>{int(r['dias_sin_medir'])} días</td></tr>" for _, r in sin_medir.iterrows())

    semana = datetime.now().isocalendar()[1]
    tabla_sm = f"""<h2 style="color:#ff9900;margin-top:30px;">⚠️ Sin medir hace más de 7 días</h2>
    <table style="width:100%;border-collapse:collapse;background:#1a1f2e;border-radius:8px;">
    <thead><tr style="background:#7a3000;color:white;">
    <th style="padding:10px;text-align:left;">Equipo</th>
    <th style="padding:10px;text-align:left;">Última medición</th>
    <th style="padding:10px;text-align:left;">Días sin medir</th>
    </tr></thead><tbody>{filas_sm}</tbody></table>""" if filas_sm else "<p style='color:#44ff88;'>✅ Todos los equipos medidos en los últimos 7 días.</p>"

    return f"""<html><body style="font-family:Arial,sans-serif;background:#0f1419;color:#e0e0e0;padding:20px;">
    <div style="max-width:720px;margin:auto;">
      <div style="background:linear-gradient(90deg,#007A3D,#00A04A);padding:20px;border-radius:12px;margin-bottom:20px;">
        <h1 style="color:white;margin:0;">GET Wear Monitor</h1>
        <p style="color:rgba(255,255,255,.85);margin:4px 0 0 0;">Reporte Semana {semana} · {date.today()}</p>
        <p style="color:rgba(255,255,255,.7);margin:2px 0 0 0;font-size:13px;">Teck QB2 · Pablo Cortés Ramos</p>
      </div>
      <h2 style="color:#00A04A;">Estado de flota</h2>
      <table style="width:100%;border-collapse:collapse;background:#1a1f2e;border-radius:8px;">
        <thead><tr style="background:#007A3D;color:white;">
          <th style="padding:10px;text-align:left;">Equipo</th>
          <th style="padding:10px;text-align:left;">Última medición</th>
          <th style="padding:10px;text-align:left;">mm</th>
          <th style="padding:10px;text-align:left;">Desgaste</th>
          <th style="padding:10px;text-align:left;">Estado</th>
          <th style="padding:10px;text-align:left;">Días a crítico</th>
        </tr></thead>
        <tbody>{filas}</tbody>
      </table>
      {tabla_sm}
      <p style="margin-top:30px;color:#555;font-size:12px;">GET Wear Monitor · Teck QB2 · Generado automáticamente</p>
    </div></body></html>"""


def enviar_correo(destinatarios: list[str], html: str, excel_data: bytes, nombre_excel: str) -> tuple[bool, str]:
    try:
        smtp_user = st.secrets.get("SMTP_USER","")
        smtp_pass = st.secrets.get("SMTP_PASS","")
        smtp_host = st.secrets.get("SMTP_HOST","smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        if not smtp_user or not smtp_pass:
            return False, "Configura SMTP_USER y SMTP_PASS en Secrets de Streamlit."
        semana = datetime.now().isocalendar()[1]
        msg = MIMEMultipart("mixed")
        msg["From"]    = smtp_user
        msg["To"]      = ", ".join(destinatarios)
        msg["Subject"] = f"GET Wear Monitor · Reporte Semana {semana} · {date.today()}"
        msg.attach(MIMEText(html, "html"))
        part = MIMEBase("application","octet-stream")
        part.set_payload(excel_data)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{nombre_excel}"')
        msg.attach(part)
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, destinatarios, msg.as_string())
        return True, "Correo enviado correctamente."
    except Exception as e:
        return False, str(e)


# =========================================================
# APP UI
# =========================================================
inject_style()
render_header()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD","")

with st.sidebar:
    st.subheader("Administración")
    admin_ok = False
    if ADMIN_PASSWORD:
        pwd = st.text_input("Clave administrador", type="password")
        admin_ok = pwd == ADMIN_PASSWORD
        if admin_ok:
            st.success("✅ Modo administrador activo")
            st.divider()
            st.markdown("**🗑️ Eliminar datos de prueba**")
            if st.button("Limpiar datos de prueba", type="primary"):
                try:
                    sb().table("mediciones").delete().in_("usuario",[
                        "Juan Pérez","Carlos Díaz","Mario Soto","Pedro Rojas",
                        "Luis Mora","Ana Torres","Roberto Lima","prueba","test","demo"
                    ]).execute()
                    cargar_historial.clear()
                    st.success("✅ Datos de prueba eliminados.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Sin clave configurada.")

tabs = st.tabs([
    "📏 Ingreso Medición",
    "🔄 Cambio de Cuchilla",
    "📋 Historial",
    "🚛 Estado Flota",
    "📂 Horómetros Excel",
    "📊 Reporte Semanal",
])


# ─────────────────────────────────────────────
# TAB 1: INGRESO MEDICIÓN
# ─────────────────────────────────────────────
with tabs[0]:
    c1, c2 = st.columns([1,1], gap="large")
    with c1:
        st.subheader("Ingreso de medición")
        equipo    = st.selectbox("Equipo", EQUIPOS, key="eq_m")
        fecha_m   = st.date_input("Fecha", value=date.today(), key="f_m")
        usuario_m = st.text_input("Técnico", key="u_m")
        st.divider()
        regla   = regla_por_equipo(equipo)
        mm_max  = REGLAS[regla]["mm_nuevo"]
        horometro_m = st.number_input("Horómetro", min_value=0.0, step=1.0, key="h_m")

        # Sugerir horómetro desde Excel si está disponible
        df_horo = cargar_horometros_db()
        if not df_horo.empty:
            row_h = df_horo[df_horo["equipo"] == equipo]
            if not row_h.empty:
                h_excel = row_h.iloc[0]["horometro_actual"]
                fecha_excel = row_h.iloc[0]["fecha"]
                st.caption(f"📊 Excel horómetros: **{h_excel:,.0f} hrs** al {fecha_excel}")

        mm_izq_m = st.number_input("Medición IZQ (mm)", min_value=0.0, value=mm_max, step=0.1, key="mi_m")
        mm_der_m = st.number_input("Medición DER (mm)", min_value=0.0, value=mm_max, step=0.1, key="md_m")
        st.caption("Se usa el valor MENOR (más crítico) para evaluar.")

        uc = ultimo_cambio_equipo(equipo)
        if uc:
            st.info(f"📌 Último cambio: {uc['fecha']} · Horómetro: {uc['horometro']:,.0f} hrs")

        if st.button("Guardar medición", type="primary", key="btn_m"):
            errores = []
            if not usuario_m.strip(): errores.append("Ingresa el nombre del técnico.")
            if horometro_m <= 0:      errores.append("Ingresa un horómetro válido.")
            mn, mx = rango_regla(regla)
            if not (mn <= mm_izq_m <= mx): errores.append(f"IZQ fuera de rango ({mn}–{mx} mm).")
            if not (mn <= mm_der_m <= mx): errores.append(f"DER fuera de rango ({mn}–{mx} mm).")
            if errores:
                for e in errores: st.error(e)
            else:
                try:
                    r = evaluar(equipo, horometro_m, mm_izq_m, mm_der_m)
                    guardar_medicion(fecha_m, equipo, horometro_m, mm_izq_m, mm_der_m, usuario_m, r)
                    st.success("✅ Medición guardada.")
                    ca, cb, cc = st.columns(3)
                    ca.metric("Estado",     f"{COLOR_ESTADO.get(r['estado'],'⚪')} {r['estado']}")
                    cb.metric("Desgaste %", f"{r['pct']:.1f}%")
                    cc.metric("mm usada",   f"{r['mm_usada']:.1f}")
                    fuente = r.get("fuente_tasa","")
                    if r.get("tasa"):    st.info(f"Tasa: **{r['tasa']} mm/h** · {fuente}")
                    elif fuente:         st.info(f"Proyección calculada desde: **{fuente}**")
                    if r.get("h_critico") is not None:
                        st.warning(f"⏱ Proyección a crítico: ~{r['h_critico']} h / ~{r['d_critico']} días")
                except Exception as e:
                    st.error(f"Error: {e}")

    with c2:
        st.subheader(f"Curva de desgaste — Equipo {equipo}")
        df_curva = cargar_historial(500)
        df_eq = df_curva[(df_curva["equipo"]==equipo) & (df_curva.get("es_cambio",pd.Series([False]*len(df_curva)))==False)].copy() if not df_curva.empty else pd.DataFrame()
        if "es_cambio" in df_eq.columns:
            df_eq = df_eq[df_eq["es_cambio"]==False]
        if not df_eq.empty and "horometro" in df_eq.columns and "mm_usada" in df_eq.columns:
            df_eq = df_eq.dropna(subset=["horometro","mm_usada"]).sort_values("horometro")
            cfg_eq = REGLAS[regla_por_equipo(equipo)]
            st.line_chart(df_eq.set_index("horometro")[["mm_usada"]], use_container_width=True)
            st.caption(f"🔴 Límite crítico: {cfg_eq['mm_critico']} mm · 🟢 GET nuevo: {cfg_eq['mm_nuevo']} mm")
        else:
            st.info("Sin datos suficientes para la curva.")

        st.subheader("Últimas mediciones")
        if not df_eq.empty:
            cols_s = [c for c in ["fecha","horometro","mm_izq","mm_der","mm_usada","condicion_pct","estado","usuario"] if c in df_eq.columns]
            st.dataframe(df_eq[cols_s].sort_values("fecha",ascending=False).head(10), use_container_width=True)
        else:
            st.info(f"Sin mediciones para equipo {equipo}.")


# ─────────────────────────────────────────────
# TAB 2: CAMBIO DE CUCHILLA (FUSIONADO)
# ─────────────────────────────────────────────
with tabs[1]:
    sub1, sub2 = st.tabs(["➕ Registrar cambio", "📋 Historial de cambios"])

    with sub1:
        st.subheader("Registrar cambio de cuchilla / GET nuevo")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            eq_c     = st.selectbox("Equipo", EQUIPOS, key="eq_c")
            fecha_c  = st.date_input("Fecha de cambio", value=date.today(), key="f_c")
            hr_c     = st.number_input("Horómetro al cambio", min_value=0.0, step=1.0, key="h_c")
            regla_c  = regla_por_equipo(eq_c)
            mm_c     = REGLAS[regla_c]["mm_critico"]
            mm_max_c = REGLAS[regla_c]["mm_nuevo"]
            mm_izq_c = st.number_input("IZQ final GET retirado (mm)", min_value=0.0, max_value=float(mm_max_c), value=float(mm_c), step=0.1, key="mi_c")
            mm_der_c = st.number_input("DER final GET retirado (mm)", min_value=0.0, max_value=float(mm_max_c), value=float(mm_c), step=0.1, key="md_c")
            virada_c = st.radio("¿Fue virada?", ["NO","SÍ"], horizontal=True, key="v_c")
            motivo_c = st.selectbox("Motivo", ["Desgaste normal","Preventivo","Daño / impacto","Campaña mantenimiento","Otro"], key="mot_c")
        with c2:
            tec1_c = st.text_input("Técnico 1", key="t1_c")
            tec2_c = st.text_input("Técnico 2 (opcional)", key="t2_c")
            obs_c  = st.text_area("Observaciones / OT generadas", height=120, key="obs_c")
            sup_c  = st.text_input("Registrado por", key="sup_c")
            st.divider()
            st.info(f"Al confirmar: ciclo nuevo con **{mm_max_c:.0f} mm**")
            if st.button("✅ Confirmar cambio", type="primary", key="btn_c"):
                errores = []
                if hr_c <= 0:          errores.append("Horómetro debe ser > 0.")
                if not tec1_c.strip(): errores.append("Ingresa al menos el Técnico 1.")
                if not sup_c.strip():  errores.append("Ingresa quién registra.")
                if errores:
                    for e in errores: st.error(e)
                else:
                    try:
                        guardar_cambio(fecha_c, eq_c, hr_c, mm_izq_c, mm_der_c,
                                       virada_c=="SÍ", motivo_c, obs_c, tec1_c, tec2_c, sup_c)
                        st.success(f"🔄 Cambio registrado · Equipo **{eq_c}** · Horómetro **{hr_c:,.0f} hrs**")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with sub2:
        st.subheader("Historial de cambios")
        df_cam = cargar_cambios()
        if not df_cam.empty:
            df_cam["fue_virada"] = df_cam["fue_virada"].map({True:"SÍ",False:"NO",1:"SÍ",0:"NO"})
            cols_c = [c for c in ["fecha","equipo","horometro","mm_izq_final","mm_der_final","fue_virada","motivo","tecnico_1","tecnico_2","observaciones","usuario"] if c in df_cam.columns]
            st.dataframe(df_cam[cols_c], use_container_width=True)
            st.download_button("⬇️ Descargar Excel", data=excel_bytes(df_cam[cols_c]), file_name="cambios.xlsx")
        else:
            st.info("Sin cambios registrados aún.")


# ─────────────────────────────────────────────
# TAB 3: HISTORIAL
# ─────────────────────────────────────────────
with tabs[2]:
    st.subheader("📋 Historial completo")
    df_h = cargar_historial()
    if not df_h.empty:
        cf1, cf2 = st.columns(2)
        with cf1: eq_fil  = st.multiselect("Equipo",  sorted(df_h["equipo"].unique()), key="fil_eq")
        with cf2: est_fil = st.multiselect("Estado", sorted(df_h["estado"].dropna().unique()), key="fil_est")
        df_sh = df_h.copy()
        if eq_fil:  df_sh = df_sh[df_sh["equipo"].isin(eq_fil)]
        if est_fil: df_sh = df_sh[df_sh["estado"].isin(est_fil)]
        cols_h = [c for c in ["fecha","equipo","horometro","mm_izq","mm_der","mm_usada","condicion_pct","estado","usuario"] if c in df_sh.columns]
        st.dataframe(df_sh[cols_h], use_container_width=True)
        st.download_button("⬇️ Descargar Excel", data=excel_bytes(df_sh[cols_h]), file_name="historial.xlsx")
    else:
        st.info("Sin mediciones aún.")


# ─────────────────────────────────────────────
# TAB 4: ESTADO FLOTA
# ─────────────────────────────────────────────
with tabs[3]:
    st.subheader("🚛 Estado de flota")
    df_flota = cargar_historial(5000)
    ultimos  = ultimos_por_equipo(df_flota)

    if not ultimos.empty:
        ec = ultimos["estado"].value_counts()
        k1,k2,k3,k4 = st.columns(4)
        k1.metric("🟢 OK",               int(ec.get("OK",0)))
        k2.metric("🟡 Monitoreo",         int(ec.get("MEDIO",0)))
        k3.metric("🟠 Programar cambio",  int(ec.get("ALTO",0)))
        k4.metric("🔴 Crítico",           int(ec.get("CRÍTICO",0)))

        st.divider()
        st.subheader("Desgaste por equipo (%)")
        if "condicion_pct" in ultimos.columns:
            ranking = ultimos[["equipo","condicion_pct"]].sort_values("condicion_pct",ascending=False).set_index("equipo")
            st.bar_chart(ranking)

        st.divider()
        st.subheader("Días sin medición")
        df_dias = dias_sin_medicion(df_flota)
        def color_dias(val):
            if pd.isna(val): return "color:gray"
            if val > 14: return "color:#ff4444;font-weight:bold"
            if val > 7:  return "color:#ff9900"
            return "color:#44ff88"
        st.dataframe(df_dias.style.applymap(color_dias, subset=["dias_sin_medir"]), use_container_width=True)

        st.divider()
        st.subheader("Proyección de cambios")
        cols_p = [c for c in ["equipo","mm_usada","condicion_pct","estado","tasa_mm_h","horas_a_critico","dias_a_critico"] if c in ultimos.columns]
        proy = ultimos[cols_p].sort_values("horas_a_critico", na_position="last") if "horas_a_critico" in cols_p else ultimos[cols_p]
        st.dataframe(proy, use_container_width=True)
    else:
        st.info("Sin datos de flota aún.")


# ─────────────────────────────────────────────
# TAB 5: HORÓMETROS EXCEL ← NUEVO
# ─────────────────────────────────────────────
with tabs[4]:
    st.subheader("📂 Carga de horómetros desde Excel")
    st.caption(
        "Sube el archivo **Control_Horómetro_TMF_Rev10.xlsm** para actualizar el horómetro actual "
        "y los promedios h/día de cada equipo. Esto mejora la proyección cuando no hay mediciones recientes."
    )

    archivo = st.file_uploader("Seleccionar archivo Excel (.xlsm / .xlsx)", type=["xlsm","xlsx"], key="upload_horo")

    if archivo is not None:
        try:
            df_preview = leer_excel_horometros(archivo)
            if df_preview.empty:
                st.warning("No se encontraron equipos GET en el archivo. Verifica que sea el archivo correcto.")
            else:
                st.success(f"✅ Se encontraron **{len(df_preview)} equipos** en el Excel.")
                cols_show = ["equipo","fecha","horometro_actual","promedio_7d","promedio_30d","promedio_historico"]
                st.dataframe(df_preview[cols_show], use_container_width=True)

                if st.button("💾 Guardar horómetros en base de datos", type="primary", key="btn_guardar_horo"):
                    n = guardar_horometros(df_preview)
                    st.success(f"✅ {n} equipos actualizados en Supabase.")
                    st.rerun()
        except Exception as e:
            st.error(f"Error leyendo el archivo: {e}")

    st.divider()
    st.subheader("Último horómetro cargado por equipo")
    df_horo_db = cargar_horometros_db()
    if not df_horo_db.empty:
        cols_h = [c for c in ["equipo","fecha","horometro_actual","promedio_7d","promedio_30d","promedio_historico"] if c in df_horo_db.columns]
        st.dataframe(df_horo_db[cols_h].sort_values("equipo"), use_container_width=True)
    else:
        st.info("Sin horómetros cargados aún. Sube el Excel para comenzar.")


# ─────────────────────────────────────────────
# TAB 6: REPORTE SEMANAL
# ─────────────────────────────────────────────
with tabs[5]:
    st.subheader("📊 Reporte Semanal")
    df_rep    = cargar_historial(5000)
    ultimos_r = ultimos_por_equipo(df_rep)
    df_dias_r = dias_sin_medicion(df_rep)
    semana    = datetime.now().isocalendar()[1]

    st.markdown(f"**Semana {semana} · {date.today()}**")

    if not ultimos_r.empty:
        st.markdown("#### Estado actual de flota")
        for _, row in ultimos_r.iterrows():
            estado = str(row.get("estado",""))
            bg     = BG_ESTADO.get(estado,"#1a1f2e")
            icon   = COLOR_ESTADO.get(estado,"⚪")
            mm     = f"{row['mm_usada']:.1f} mm" if pd.notna(row.get("mm_usada")) else "—"
            pct    = f"{row['condicion_pct']:.1f}%" if pd.notna(row.get("condicion_pct")) else "—"
            dias_c = f"{row['dias_a_critico']:.0f} días" if pd.notna(row.get("dias_a_critico")) else "—"
            st.markdown(
                f'<div class="equipo-card" style="background:{bg};">'
                f'<b>Equipo {row["equipo"]}</b> &nbsp;|&nbsp; {icon} {estado} &nbsp;|&nbsp;'
                f' {mm} &nbsp;|&nbsp; Desgaste: {pct} &nbsp;|&nbsp; Días a crítico: {dias_c}'
                f'</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Equipos sin medir (> 7 días)")
        sin_medir_r = df_dias_r[df_dias_r["dias_sin_medir"].notna() & (df_dias_r["dias_sin_medir"] > 7)]
        if not sin_medir_r.empty:
            st.dataframe(sin_medir_r, use_container_width=True)
        else:
            st.success("✅ Todos los equipos medidos en los últimos 7 días.")

        st.divider()
        st.markdown("#### Enviar reporte por correo")
        dest_input = st.text_input("Destinatarios (separados por coma)", value="Pablo.cortes2@teck.com", key="dest_mail")

        col_prev, col_env = st.columns(2)
        with col_prev:
            if st.button("👁️ Ver preview", key="btn_prev"):
                html_prev = generar_html_reporte(ultimos_r, df_dias_r)
                st.components.v1.html(html_prev, height=600, scrolling=True)
        with col_env:
            if st.button("📧 Enviar reporte", type="primary", key="btn_mail"):
                dests = [d.strip() for d in dest_input.split(",") if d.strip()]
                if not dests:
                    st.error("Ingresa al menos un destinatario.")
                else:
                    cols_xl = [c for c in ["equipo","fecha","mm_usada","condicion_pct","estado","tasa_mm_h","dias_a_critico"] if c in ultimos_r.columns]
                    ok, msg = enviar_correo(dests, generar_html_reporte(ultimos_r, df_dias_r),
                                           excel_bytes(ultimos_r[cols_xl]),
                                           f"GET_Wear_S{semana}_{date.today()}.xlsx")
                    if ok: st.success(f"✅ {msg}")
                    else:  st.error(f"❌ {msg}")

        st.download_button("⬇️ Descargar Excel reporte",
            data=excel_bytes(ultimos_r),
            file_name=f"reporte_semana_{semana}.xlsx")
    else:
        st.info("Sin datos para generar reporte.")
