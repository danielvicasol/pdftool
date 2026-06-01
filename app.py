import streamlit as st
import json
import base64
import io
from PyPDF2 import PdfReader, PdfWriter

st.title("PDF → JSON (páginas en Base64)")

uploaded_file = st.file_uploader("Sube un PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)

    paginas = []

    # Procesar cada página
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        # Guardar la página en memoria (no en disco)
        buffer = io.BytesIO()
        writer.write(buffer)

        # Convertir a bytes
        pdf_bytes = buffer.getvalue()

        # Codificar a base64
        base64_page = base64.b64encode(pdf_bytes).decode("utf-8")

        paginas.append({
            "pagina": i + 1,
            "base64": base64_page
        })

    resultado = {
        "total_paginas": len(paginas),
        "paginas": paginas
    }

    # Mostrar JSON
    st.json(resultado)

    # Descargar JSON
    st.download_button(
        label="Descargar JSON",
        data=json.dumps(resultado, indent=4),
        file_name="pdf_base64.json",
        mime="application/json"
    )
