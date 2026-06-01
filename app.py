import streamlit as st
import json
import base64
import io
from pypdf import PdfReader, PdfWriter  # recomendado en lugar de PyPDF2

st.title("PDF → JSON (Base64 por página)")

uploaded_file = st.file_uploader("Sube un PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)

    paginas = []

    # Procesar páginas
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

    resultado = {
        "total_paginas": len(paginas),
        "paginas": paginas
    }

    # ✅ SOLO info básica (no JSON completo)
    st.success(f"PDF procesado correctamente ✅")
    st.write(f"Total de páginas: {len(paginas)}")

    # ✅ BOTÓN DE DESCARGA (clave)
    json_bytes = json.dumps(resultado).encode("utf-8")

    st.download_button(
        label="Descargar JSON",
        data=json_bytes,
        file_name="pdf_base64.json",
        mime="application/json"
    )
