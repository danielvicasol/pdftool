import streamlit as st
import json
import base64
import io
from PyPDF2 import PdfReader, PdfWriter

st.set_page_config(page_title="PDF → JSON Base64", layout="wide")

# -----------------------------
# Estado
# -----------------------------
if "resultado" not in st.session_state:
    st.session_state.resultado = None

if "json_bytes" not in st.session_state:
    st.session_state.json_bytes = None

if "pdf_procesado" not in st.session_state:
    st.session_state.pdf_procesado = False

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def limpiar_app():
    st.session_state.resultado = None
    st.session_state.json_bytes = None
    st.session_state.pdf_procesado = False
    st.session_state.uploader_key += 1


st.title("📄 PDF → JSON (Base64 por página)")

uploaded_file = st.file_uploader(
    "Sube un PDF",
    type="pdf",
    key=f"pdf_uploader_{st.session_state.uploader_key}"
)

# -----------------------------
# PROCESAR PDF
# -----------------------------
if uploaded_file is not None and not st.session_state.pdf_procesado:

    with st.spinner("Procesando PDF... ⏳", show_time=True):

        reader = PdfReader(uploaded_file)
        total_paginas = len(reader.pages)

        paginas = []
        progress_bar = st.progress(0)
        progress_text = st.empty()

        for i, page in enumerate(reader.pages):

            writer = PdfWriter()
            writer.add_page(page)

            buffer = io.BytesIO()
            writer.write(buffer)

            pdf_bytes = buffer.getvalue()
            base64_page = base64.b64encode(pdf_bytes).decode("utf-8")

            paginas.append({
                "pagina": i + 1,
                "base64": base64_page
            })

            progreso = (i + 1) / total_paginas
            progress_bar.progress(progreso)
            progress_text.write(f"Procesando página {i+1} de {total_paginas}")

        progress_bar.empty()
        progress_text.empty()

        resultado = {
            "total_paginas": total_paginas,
            "paginas": paginas
        }

        st.session_state.resultado = resultado
        st.session_state.json_bytes = json.dumps(resultado).encode("utf-8")
        st.session_state.pdf_procesado = True

    st.success("✅ PDF procesado correctamente")
    st.write(f"Total de páginas: {total_paginas}")

# -----------------------------
# DESCARGA + LIMPIEZA
# -----------------------------
if st.session_state.pdf_procesado:

    # Spinner justo antes de descargar (UX simulada)
    if st.button("📥 Preparar descarga y limpiar"):
        with st.spinner("Preparando descarga... ⏳"):
            pass  # solo UX, no bloquea realmente

    st.download_button(
        label="📥 Descargar JSON",
        data=st.session_state.json_bytes,
        file_name="pdf_base64.json",
        mime="application/json",
        on_click=limpiar_app
    )
