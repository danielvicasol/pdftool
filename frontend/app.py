import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="PDF → JSON Base64", layout="wide")
st.title("📄 PDF → JSON (backend API + descarga real)")

if "job" not in st.session_state:
    st.session_state.job = None

uploaded_file = st.file_uploader("Sube un PDF", type="pdf")

if uploaded_file is not None:
    st.write(f"Archivo: **{uploaded_file.name}**")

    if st.button("Procesar en backend"):
        with st.spinner("Subiendo y procesando PDF en backend... ⏳", show_time=True):
            files = {
                "file": (uploaded_file.name, uploaded_file, "application/pdf")
            }
            response = requests.post(f"{BACKEND_URL}/convert", files=files, timeout=None)
            response.raise_for_status()
            st.session_state.job = response.json()

if st.session_state.job:
    st.success("✅ PDF procesado")
    st.write(f"Total páginas: {st.session_state.job['total_paginas']}")

    download_url = f"{BACKEND_URL}{st.session_state.job['download_path']}"

    st.link_button("📥 Descargar JSON (stream real)", download_url)
    st.caption("La descarga la sirve el backend directamente. Tras enviarse, el backend limpia los temporales.")
