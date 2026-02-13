import streamlit as st
from deep_translator import GoogleTranslator
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TraductorProAI", page_icon="🌐", layout="wide")

# --- FUNCIONES ---
def extraer_texto_pdf(archivo):
    doc = fitz.open(stream=archivo.read(), filetype="pdf")
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto

def dividir_por_caracteres(texto, max_caracteres=4500):
    """Google Translator tiene un límite de 5000 caracteres por pedazo"""
    return [texto[i:i + max_caracteres] for i in range(0, len(texto), max_caracteres)]

def crear_docx(texto_traducido):
    doc = Document()
    doc.add_heading('Traducción - TraductorProAI', 0)
    for linea in texto_traducido.split('\n'):
        if linea.strip():
            doc.add_paragraph(linea)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFAZ ---
st.title("🌐 TraductorProAI (Versión Estable)")
st.markdown("### Traducción ilimitada y gratuita sin API Keys")

archivo_pdf = st.file_uploader("Carga tu archivo PDF", type=["pdf"])
idioma_opciones = {
    "Inglés": "en",
    "Español": "es",
    "Francés": "fr",
    "Alemán": "de",
    "Italiano": "it",
    "Portugués": "pt"
}
idioma_elegido = st.selectbox("Selecciona el idioma de destino", list(idioma_opciones.keys()))

if archivo_pdf and st.button("🚀 Traducir Ahora"):
    with st.spinner("Procesando documento..."):
        try:
            # 1. Extraer
            texto_completo = extraer_texto_pdf(archivo_pdf)
            
            # 2. Dividir para no superar el límite de Google
            fragmentos = dividir_por_caracteres(texto_completo)
            
            # 3. Traducir
            traductor = GoogleTranslator(source='auto', target=idioma_opciones[idioma_elegido])
            
            traduccion_final = ""
            progreso = st.progress(0)
            
            for idx, frag in enumerate(fragmentos):
                resultado = traductor.translate(frag)
                traduccion_final += resultado + "\n"
                progreso.progress((idx + 1) / len(fragmentos))
            
            st.success("✅ ¡Traducción completada!")
            
            # 4. Descarga
            doc_word = crear_docx(traduccion_final)
            st.download_button(
                label="📥 Descargar Word (.docx)",
                data=doc_word,
                file_name=f"Traduccion_{idioma_elegido}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            with st.expander("Ver previsualización"):
                st.write(traduccion_final)

        except Exception as e:
            st.error(f"Ocurrió un error inesperado: {e}")
