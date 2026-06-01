import streamlit as st
import json
import base64
import io
from PyPDF2 import PdfReader, PdfWriter  # usa PyPDF2 si ya lo tienes en requirements

st.set_page_config(page_title="PDF → JSON Base64", layout="wide")

st.title("📄 PDF → JSON (Base64 por página)")

uploaded_file = st.file_uploader("Sube un PDF", type="pdf")

if uploaded_file is not None:

    # Spinner + progreso
    with st.spinner("Procesando PDF... ⏳"):

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

            # ✅ actualizar progreso
            progreso = (i + 1) / total_paginas
            progress_bar.progress(progreso)
            progress_text.write(f"Procesando página {i+1} de {total_paginas}")

    # ✅ limpiar barra (opcional)
    progress_bar.empty()
    progress_text.empty()

    # ✅ resultado final
    resultado = {
        "total_paginas": total_paginas,
        "paginas": paginas
    }

    # ✅ mensaje final
    st.success("✅ PDF procesado correctamente")
    st.write(f"Total de páginas: {total_paginas}")

    # ✅ SOLO descarga (sin render del JSON grande)
    json_bytes = json.dumps(resultado).encode("utf-8")

    st.download_button(
        label="📥 Descargar JSON",
        data=json_bytes,
        file_name="pdf_base64.json",
        mime="application/json"
    )
