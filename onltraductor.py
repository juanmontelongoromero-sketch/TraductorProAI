import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
import time

st.set_page_config(page_title="TraductorProAI", page_icon="🌐", layout="wide")

with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Introduce tu Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)


def extraer_texto_pdf(archivo):
    doc = fitz.open(stream=archivo.read(), filetype="pdf")
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto

def dividir_texto(texto, limite_palabras=3000):
    palabras = texto.split()
    for i in range(0, len(palabras), limite_palabras):
        yield " ".join(palabras[i:i + limite_palabras])

def traducir_bloque(modelo, bloque, idioma_destino):
    prompt = f"Traduce el siguiente texto al {idioma_destino}. Solo entrega la traducción:\n\n{bloque}"
    response = modelo.generate_content(prompt)
    return response.text

def crear_docx(texto_traducido):
    doc = Document()
    for linea in texto_traducido.split('\n'):
        doc.add_paragraph(linea)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.title("🌐 TraductorProAI")
st.subheader("Traducción profesional a Word con Inteligencia Artificial")

if not api_key:
    st.warning("⚠️ Por favor, introduce tu API Key en la barra lateral para comenzar.")
else:
    archivo_pdf = st.file_uploader("Sube tu archivo PDF", type=["pdf"])
    idioma_destino = st.selectbox("Selecciona el idioma de destino", ["Inglés", "Español", "Francés", "Alemán", "Italiano"])

    if archivo_pdf and st.button("🚀 Iniciar Traducción"):
        texto_completo = extraer_texto_pdf(archivo_pdf)
        bloques = list(dividir_texto(texto_completo))
        
        st.info(f"Procesando {len(bloques)} fragmentos del documento...")
        
        traduccion_final = ""
        barra_progreso = st.progress(0)
        modelo = genai.GenerativeModel('gemini-1.5-flash')

        for idx, bloque in enumerate(bloques):
            with st.spinner(f"Traduciendo fragmento {idx + 1}..."):
                parte_traducida = traducir_bloque(modelo, bloque, idioma_destino)
                traduccion_final += parte_traducida + "\n"
                barra_progreso.progress((idx + 1) / len(bloques))
                time.sleep(1)

        st.success("¡Traducción completada con éxito!")

        archivo_word = crear_docx(traduccion_final)

        st.download_button(
            label="📄 Descargar traducción en Word (.docx)",
            data=archivo_word,
            file_name="Traduccion_TraductorProAI.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )