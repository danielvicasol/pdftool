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
    """Limpia el PDF subido y el resultado generado de la app."""
    st.session_state.resultado = None
    st.session_state.json_bytes = None
    st.session_state.pdf_procesado = False

    # Limpia el file_uploader cambiando la key
    st.session_state.uploader_key += 1

    # Si el widget existe en session_state, lo quitamos
    uploader_widget_key = f"pdf_uploader_{st.session_state.uploader_key - 1}"
    if uploader_widget_key in st.session_state:
        del st.session_state[uploader_widget_key]


st.title("📄 PDF → JSON (Base64 por página)")

uploaded_file = st.file_uploader(
    "Sube un PDF",
    type="pdf",
    key=f"pdf_uploader_{st.session_state.uploader_key}"
)

# -----------------------------
# Procesado del PDF
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

        st.session_state.resultado = {
            "total_paginas": total_paginas,
            "paginas": paginas
        }
        st.session_state.pdf_procesado = True

    st.success("✅ PDF procesado correctamente")
    st.write(f"Total de páginas: {st.session_state.resultado['total_paginas']}")

# -----------------------------
# Preparación de la descarga
# -----------------------------
if st.session_state.resultado is not None:
    if st.session_state.json_bytes is None:
        if st.button("📦 Preparar descarga"):
            with st.spinner("Preparando JSON para descarga... ⏳", show_time=True):
                st.session_state.json_bytes = json.dumps(
                    st.session_state.resultado,
                    ensure_ascii=False
                ).encode("utf-8")

            st.success("✅ Descarga preparada")

    # -----------------------------
    # Botón de descarga + limpieza
    # -----------------------------
    if st.session_state.json_bytes is not None:
        st.download_button(
            label="📥 Descargar JSON y limpiar",
            data=st.session_state.json_bytes,
            file_name="pdf_base64.json",
            mime="application/json",
            on_click=limpiar_app
        )
