import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TraductorProAI", page_icon="🌐", layout="wide")

# --- SEGURIDAD: OPENAI API KEY ---
client = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
else:
    with st.sidebar:
        st.title("🔐 Configuración OpenAI")
        api_key = st.text_input("Introduce tu OpenAI API Key", type="password")
        if api_key:
            client = OpenAI(api_key=api_key)

# --- FUNCIONES DE LÓGICA ---

def extraer_texto_pdf(archivo):
    doc = fitz.open(stream=archivo.read(), filetype="pdf")
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto

def dividir_texto(texto, limite_palabras=1500):
    palabras = texto.split()
    for i in range(0, len(palabras), limite_palabras):
        yield " ".join(palabras[i:i + limite_palabras])

def traducir_con_openai(bloque, idioma_destino):
    try:
        # Usamos GPT-4o-mini: balance perfecto entre costo y calidad
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Eres un traductor experto. Traduce el siguiente texto al {idioma_destino}. Solo devuelve la traducción final, mantén el formato profesional."},
                {"role": "user", "content": bloque}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"\n[Error en OpenAI: {str(e)}]\n"

def crear_docx(texto_traducido):
    doc = Document()
    doc.add_heading('Traducción Profesional - TraductorProAI', 0)
    for parrafo in texto_traducido.split('\n'):
        if parrafo.strip():
            doc.add_paragraph(parrafo)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFAZ ---
st.title("🌐 TraductorProAI")
st.subheader("Impulsado por ChatGPT (GPT-4o)")

if not client:
    st.warning("⚠️ Por favor, configura tu API Key de OpenAI para continuar.")
else:
    archivo_pdf = st.file_uploader("Sube tu PDF para traducir", type=["pdf"])
    idioma = st.selectbox("Idioma de destino", ["Inglés", "Español", "Francés", "Alemán", "Italiano", "Portugués"])

    if archivo_pdf and st.button("🚀 Iniciar Traducción Inteligente"):
        texto_completo = extraer_texto_pdf(archivo_pdf)
        fragmentos = list(dividir_texto(texto_completo))
        
        st.info(f"Documento listo. Traduciendo en {len(fragmentos)} bloques...")
        
        traduccion_final = ""
        barra = st.progress(0)

        for idx, bloque in enumerate(fragmentos):
            with st.spinner(f"Procesando bloque {idx+1} de {len(fragmentos)}..."):
                resultado = traducir_con_openai(bloque, idioma)
                traduccion_final += resultado + "\n\n"
                barra.progress((idx + 1) / len(fragmentos))
                # OpenAI es muy rápido, con 0.5s de espera es suficiente
                time.sleep(0.5)

        st.success("✅ ¡Traducción terminada!")
        
        with st.expander("Previsualizar traducción"):
            st.write(traduccion_final)
            
        doc_word = crear_docx(traduccion_final)
        
        st.download_button(
            label="📥 Descargar Documento Word",
            data=doc_word,
            file_name=f"Traduccion_ChatGPT_{idioma}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

