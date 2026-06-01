import os
import io
import json
import uuid
import base64
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from pypdf import PdfReader, PdfWriter

app = FastAPI(title="PDF API")

BASE_TMP = Path(tempfile.gettempdir()) / "pdf_api_jobs"
BASE_TMP.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 1024 * 1024  # 1 MB


def cleanup_job(job_dir: Path):
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)


def stream_file(path: Path, chunk_size: int = CHUNK_SIZE):
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    # Validación básica
    filename = Path(file.filename or "document.pdf").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # Directorio temporal aislado por trabajo
    job_id = str(uuid.uuid4())
    job_dir = BASE_TMP / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    input_path = job_dir / filename
    output_path = job_dir / "pdf_base64.json"

    # 1) Guardar el upload por chunks a disco
    try:
        with open(input_path, "wb") as out:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                out.write(chunk)
    finally:
        await file.close()

    # 2) Procesar el PDF página a página y escribir JSON incrementalmente
    try:
        with open(input_path, "rb") as pdf_fp:
            reader = PdfReader(pdf_fp)
            total_paginas = len(reader.pages)

            with open(output_path, "w", encoding="utf-8") as out_json:
                out_json.write('{"total_paginas":')
                out_json.write(str(total_paginas))
                out_json.write(',"paginas":[')

                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)

                    # Aquí solo mantienes una página en memoria, no todo el documento
                    page_buf = io.BytesIO()
                    writer.write(page_buf)
                    page_bytes = page_buf.getvalue()
                    page_b64 = base64.b64encode(page_bytes).decode("utf-8")

                    record = {
                        "pagina": i + 1,
                        "base64": page_b64
                    }

                    if i > 0:
                        out_json.write(",")

                    json.dump(record, out_json, ensure_ascii=False)

                out_json.write("]}")
    except Exception as e:
        cleanup_job(job_dir)
        raise HTTPException(status_code=500, detail=f"Error procesando el PDF: {e}")

    return {
        "job_id": job_id,
        "download_path": f"/download/{job_id}",
        "total_paginas": total_paginas
    }


@app.get("/download/{job_id}")
async def download_result(job_id: str):
    job_dir = BASE_TMP / job_id
    output_path = job_dir / "pdf_base64.json"

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Resultado no encontrado o ya descargado")

    headers = {
        "Content-Disposition": 'attachment; filename="pdf_base64.json"'
    }

    # Descarga real por streaming + limpieza al finalizar la respuesta
    return StreamingResponse(
        stream_file(output_path),
        media_type="application/json",
        headers=headers,
        background=BackgroundTask(cleanup_job, job_dir)
    )
