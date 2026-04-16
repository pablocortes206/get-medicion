import streamlit as st
from datetime import date

st.set_page_config(page_title="GET Wear Monitor", layout="wide")

st.title("GET Wear Monitor 🚜")

# =========================
# FORMULARIO MEDICIÓN
# =========================

st.subheader("Ingreso de medición")

equipo = st.selectbox("Equipo", ["101", "102", "103", "201", "301"])

fecha_medicion = st.date_input("Fecha de medición", value=date.today())

horometro = st.number_input("Horómetro", min_value=0.0, step=1.0)

mm_izq = st.number_input("Medición IZQ (mm)", min_value=0.0, step=0.1)
mm_der = st.number_input("Medición DER (mm)", min_value=0.0, step=0.1)

usuario = st.text_input("Usuario")

if st.button("Guardar medición"):
    st.success(f"Medición guardada para equipo {equipo}")
    st.write({
        "equipo": equipo,
        "fecha": fecha_medicion,
        "horometro": horometro,
        "mm_izq": mm_izq,
        "mm_der": mm_der,
        "usuario": usuario
    })
