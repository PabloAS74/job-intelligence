import streamlit as st
import requests

API_URL = "http://localhost:8000/api"

st.set_page_config(page_title="Job Intelligence", page_icon="💼", layout="wide")
st.title("💼 Job Intelligence Dashboard")

# 1. Creamos las pestañas y las guardamos en variables
tab_analitica, tab_ofertas = st.tabs(["📊 Analítica de Mercado", "🔍 Buscador de Ofertas"])

# 2. Contenido de la primera pestaña
with tab_analitica:
    st.header("🏆 Top Empresas Contratando")
    try:
        response_stats = requests.get(f"{API_URL}/stats/top-companies?limit=5")
        if response_stats.status_code == 200:
            top_companies = response_stats.json()
            cols = st.columns(len(top_companies))
            for i, col in enumerate(cols):
                empresa = top_companies[i]
                col.metric(label=empresa["company"]["name"], value=f"{empresa['job_count']} ofertas")
    except Exception:
        st.error("Error conectando a la API.")

# 3. Contenido de la segunda pestaña
with tab_ofertas:
    st.header("🔍 Ofertas Recientes")
    dias = st.slider("Filtro de antigüedad (días)", min_value=0, max_value=30, value=7)
    
    try:
        response_jobs = requests.get(f"{API_URL}/jobs?days={dias}&limit=20")
        if response_jobs.status_code == 200:
            jobs = response_jobs.json()
            if jobs:
                for job in jobs:
                    empresa_nombre = job["company"]["name"] if job.get("company") else "Empresa oculta"
                    ubicacion = job["location"]["city"] if job.get("location") else "Remoto"
                    
                    with st.expander(f"{job['title']} en **{empresa_nombre}**"):
                        st.write(f"📍 **Ubicación:** {ubicacion}")
                        st.write(f"🗓️ **Publicado:** {job['published_at']}")
            else:
                st.info(f"No hay ofertas en los últimos {dias} días.")
    except Exception:
        st.error("Error al cargar las ofertas.")