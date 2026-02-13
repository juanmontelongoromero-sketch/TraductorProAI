import streamlit as st
import requests
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

st.set_page_config(page_title="TraductorProAI", page_icon="🌐", layout="wide")

# --- CONFIGURACIÓN HUGGING FACE ---
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def consultar_ia(texto, idioma):
    prompt = f"Translate the following text to {idioma}. Only return the translation, no comments:\n\n{texto}"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 1000}}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    resultado = response.json()
    
    # Extraer el texto de la respuesta
    if isinstance(resultado, list) and 'generated_text' in resultado[0]:
        return resultado[0]['generated_text'].replace(prompt, "").strip()
    return "[Error de conexión con la IA]"

# --- FUNCIONES DE DOCUMENTO ---
def extraer_texto_pdf(archivo):
    doc = fitz.open(stream=archivo.read(), filetype="pdf")
    return "\n".join([p.get_text() for p in doc])

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
st.title("🌐 TraductorProAI (Open Source)")
st.subheader("Traducción gratuita usando modelos de Hugging Face")

archivo = st.file_uploader("Sube tu PDF", type=["pdf"])
idioma = st.selectbox("Idioma destino", ["Spanish", "English", "French", "German", "Italian"])

if archivo and st.button("🚀 Traducir con IA"):
    with st.spinner("La IA está trabajando..."):
        texto_original = extraer_texto_pdf(archivo)
        # Por seguridad con modelos gratis, enviamos los primeros 2000 caracteres
        traduccion = consultar_ia(texto_original[:2000], idioma)
        
        st.success("✅ ¡Traducción lista!")
        st.text_area("Resultado:", traduccion, height=300)
        
        doc_word = crear_docx(traduccion)
        st.download_button("📥 Descargar Word", doc_word, "Traduccion_IA.docx")


