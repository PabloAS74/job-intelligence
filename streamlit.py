import streamlit as st
import requests

API_URL = "http://localhost:8000/api"

# Configuración de la página
st.set_page_config(page_title="Job Intelligence", page_icon="💼", layout="wide")

st.title("💼 Job Intelligence Dashboard")
st.markdown("Explora las últimas ofertas y descubre qué empresas están contratando más.")

# --- SECCIÓN 1: Analítica (Top Empresas) ---
st.header("Top Empresas Contratando")

try:
    # Llamamos a nuestro endpoint analítico
    response_stats = requests.get(f"{API_URL}/stats/top-companies?limit=5")
    if response_stats.status_code == 200:
        top_companies = response_stats.json()
        
        # Creamos columnas visuales para las métricas
        cols = st.columns(len(top_companies))
        for i, col in enumerate(cols):
            empresa = top_companies[i]
            # Usamos st.metric que queda súper profesional
            col.metric(
                label=empresa["company"]["name"], 
                value=f"{empresa['job_count']} ofertas"
            )
except Exception as e:
    st.error(f"Error conectando a la API: Asegúrate de que FastAPI está encendido.")

st.divider()

# --- SECCIÓN 2: Listado de Novedades ---
st.header("Ofertas Recientes")

# Un slider interactivo para el parámetro 'days' de tu API
dias = st.slider("Filtro de antigüedad (días)", min_value=0, max_value=30, value=7)

try:
    # Llamamos a nuestro endpoint de listado con el parámetro days
    response_jobs = requests.get(f"{API_URL}/jobs?days={dias}&limit=20")
    if response_jobs.status_code == 200:
        jobs = response_jobs.json()
        
        if jobs:
            # Mostramos cada oferta en un bloque desplegable (expander)
            for job in jobs:
                empresa_nombre = job["company"]["name"] if job.get("company") else "Empresa oculta"
                ubicacion = job["location"]["city"] if job.get("location") else "Remoto"
                
                with st.expander(f"{job['title']} en **{empresa_nombre}**"):
                    st.write(f"📍 **Ubicación:** {ubicacion}")
                    st.write(f"🗓️ **Publicado:** {job['published_at']}")
                    st.write(f"🏷️ **Modalidad:** {job.get('remote_type', 'N/A')} | {job.get('employment_type', 'N/A')}")
                    
                    # Un botoncito simulado
                    st.button("Ver detalle completo", key=f"btn_{job['id']}")
        else:
            st.info(f"No hay ofertas publicadas en los últimos {dias} días.")
except Exception as e:
    st.error("Error al cargar las ofertas.")