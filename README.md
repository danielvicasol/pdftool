# 📄 PDF to JSON (Base64 Pages) - Streamlit App

Aplicación web sencilla desarrollada con **Streamlit** que permite:

✅ Subir un archivo PDF  
✅ Separarlo en páginas individuales  
✅ Convertir cada página a **Base64**  
✅ Generar un **JSON estructurado**  
✅ Descargar el resultado  

---

## 🚀 Demo funcional

El flujo de la aplicación es:

1. Subes un PDF desde el navegador
2. La app lo procesa en memoria
3. Separa cada página
4. Convierte cada página a Base64
5. Devuelve un JSON listo para consumir en APIs o pipelines de IA

---

## 🧠 Caso de uso

Esta herramienta está especialmente pensada para:

- Integraciones con APIs (que requieren texto, no binario)
- Sistemas de almacenamiento en JSON
- Pipelines de IA / RAG
- Automatización documental
- Microservicios de procesamiento de documentos

---

## ⚙️ Tecnologías utilizadas

- **Python**
- **Streamlit** (frontend web)
- **PyPDF2** (procesamiento de PDF)
- **Base64** (codificación binaria a texto)

---

## 📦 Instalación

Clona el repositorio:

```bash
git clone https://github.com/tuusuario/pdf-base64-streamlit.git
cd pdf-base64-streamlit
