import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
import time

st.set_page_config(page_title="TraductorProAI", page_icon="🌐", layout="wide")

# --- CONEXIÓN SEGURA ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    api_key = True
else:
    st.error("⚠️ Configura la GEMINI_API_KEY en los Secrets de Streamlit.")
    api_key = False

# --- EL TRUCO PARA EVITAR EL "NOT FOUND" ---
def traducir_bloque(bloque, idioma_destino):
    # Lista de nombres posibles para el mismo modelo
    modelos_disponibles = [
        'gemini-1.5-flash', 
        'models/gemini-1.5-flash', 
        'gemini-pro',
        'models/gemini-pro'
    ]
    
    for nombre in modelos_disponibles:
        try:
            model = genai.GenerativeModel(nombre)
            prompt = f"Traduce este texto al {idioma_destino}. Solo entrega la traducción:\n\n{bloque}"
            response = model.generate_content(prompt)
            if response.text:
                return response.text
        except Exception:
            continue # Si este nombre falla, intenta con el siguiente
    return "[Error: Google no respondió. Revisa si tu API Key es válida en Google AI Studio]"

# --- FUNCIONES DE DOCUMENTO ---
def extraer_texto_pdf(archivo):
    doc = fitz.open(stream=archivo.read(), filetype="pdf")
    return "\n".join([pagina.get_text() for pagina in doc])

def dividir_en_trozos(texto, palabras=800): # Trozos más pequeños son más seguros
    lineas = texto.split()
    for i in range(0, len(lineas), palabras):
        yield " ".join(lineas[i:i + palabras])

def crear_docx(texto):
    doc = Document()
    doc.add_heading('Traducción TraductorProAI', 0)
    for p in texto.split('\n'):
        if p.strip(): doc.add_paragraph(p)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- INTERFAZ ---
st.title("🌐 TraductorProAI (Versión Gratuita)")

if api_key:
    archivo = st.file_uploader("Sube tu PDF", type=["pdf"])
    idioma = st.selectbox("Idioma", ["Inglés", "Español", "Francés", "Alemán", "Italiano"])

    if archivo and st.button("🚀 Traducir Ahora"):
        texto_original = extraer_texto_pdf(archivo)
        trozos = list(dividir_en_trozos(texto_original))
        
        traduccion_final = ""
        progreso = st.progress(0)
        
        for idx, trozo in enumerate(trozos):
            with st.spinner(f"Traduciendo parte {idx+1} de {len(trozos)}..."):
                resultado = traducir_bloque(trozo, idioma)
                traduccion_final += resultado + "\n\n"
                progreso.progress((idx + 1) / len(trozos))
                # IMPORTANTE: Google gratis pide paciencia (4 segundos entre partes)
                time.sleep(4) 

        st.success("✅ ¡Listo!")
        doc_final = crear_docx(traduccion_final)
        st.download_button("📥 Descargar Word", doc_final, "Traduccion_Final.docx")

