from datetime import datetime

import requests
from bs4 import BeautifulSoup

import streamlit as st

API_URL = "http://localhost:8000/api"
REQUEST_TIMEOUT = 10

REMOTE_LABELS = {
    "remote": "Remoto",
    "hybrid": "Híbrido",
    "on-site": "Presencial",
}
EMPLOYMENT_LABELS = {
    "full-time": "Jornada completa",
    "part-time": "Jornada parcial",
    "contract": "Contrato",
    "freelance": "Freelance",
    "internship": "Prácticas",
}
EXPERIENCE_LABELS = {
    "junior": "Junior",
    "mid": "Intermedio",
    "senior": "Senior",
    "lead": "Lead",
    "executive": "Dirección",
}


def api_get(path: str, params: dict | None = None) -> requests.Response:
    """Realiza una petición a la API con un timeout común."""
    response = requests.get(
        f"{API_URL}/{path.lstrip('/')}", params=params, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response


def format_date(value: str | None) -> str:
    if not value:
        return "Sin fecha"
    try:
        return datetime.fromisoformat(value).strftime("%d/%m/%Y")
    except ValueError:
        return value


def format_salary(job: dict) -> str:
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    currency = job.get("salary_currency") or ""

    if salary_min is None and salary_max is None:
        return "No indicado"
    if salary_min is not None and salary_max is not None:
        amount = f"{salary_min:,.0f} – {salary_max:,.0f}"
    elif salary_min is not None:
        amount = f"Desde {salary_min:,.0f}"
    else:
        amount = f"Hasta {salary_max:,.0f}"
    return f"{amount} {currency}".strip().replace(",", ".")


def format_location(location: dict | None) -> str:
    if not location:
        return "No indicada"
    parts = [location.get("city"), location.get("region"), location.get("country")]
    unique_parts = list(dict.fromkeys(part for part in parts if part))
    return ", ".join(unique_parts) or "No indicada"


def clean_description(description: str | None) -> str:
    """Convierte la descripción recibida de la API en texto legible."""
    if not description:
        return "Esta oferta no incluye una descripción."

    text = BeautifulSoup(description, "html.parser").get_text(separator="\n", strip=True)
    lines = (line.strip() for line in text.splitlines())
    clean_text = "\n\n".join(line for line in lines if line)
    return clean_text or "Esta oferta no incluye una descripción."


@st.dialog("Detalle completo de la oferta", width="large")
def render_job_details(job_id: int) -> None:
    with st.spinner("Cargando detalle..."):
        try:
            detail = api_get(f"jobs/{job_id}").json()
        except (requests.RequestException, ValueError):
            st.error("No se han podido cargar los detalles de esta oferta.")
            return

    st.subheader(detail.get("title") or "Oferta sin título")
    company = detail.get("company") or {}
    st.caption(company.get("name") or "Empresa no indicada")

    st.markdown("#### Descripción")
    st.write(clean_description(detail.get("description")))

    detail_col_1, detail_col_2 = st.columns(2)
    detail_col_1.markdown(
        f"**Experiencia:** {EXPERIENCE_LABELS.get(detail.get('experience_level'), 'No indicada')}"
    )
    detail_col_1.markdown(
        f"**Fuente:** {(detail.get('source') or 'No indicada').title()}"
    )
    detail_col_2.markdown(
        f"**Primera vez vista:** {format_date(detail.get('first_seen_at'))}"
    )
    detail_col_2.markdown(
        f"**Última vez vista:** {format_date(detail.get('last_seen_at'))}"
    )

    if detail.get("url"):
        st.link_button("Ir a la oferta original ↗", detail["url"])


def render_job_card(job: dict) -> None:
    company = job.get("company") or {}
    role = job.get("role") or {}

    with st.container(border=True):
        st.subheader(job.get("title") or "Oferta sin título")
        st.markdown(f"**{company.get('name') or 'Empresa no indicada'}**")

        info_col_1, info_col_2, info_col_3 = st.columns(3)
        info_col_1.markdown(
            f"📍 **Ubicación**  \n{format_location(job.get('location'))}"
        )
        info_col_1.markdown(
            f"🧭 **Modalidad**  \n{REMOTE_LABELS.get(job.get('remote_type'), 'No indicada')}"
        )
        info_col_2.markdown(f"💼 **Rol**  \n{role.get('name') or 'No indicado'}")
        info_col_2.markdown(
            f"🕒 **Contrato**  \n{EMPLOYMENT_LABELS.get(job.get('employment_type'), 'No indicado')}"
        )
        info_col_3.markdown(f"💰 **Salario**  \n{format_salary(job)}")
        info_col_3.markdown(
            f"📅 **Publicada**  \n{format_date(job.get('published_at'))}"
        )

        if st.button(
            "Ver detalle completo", key=f"job-details-{job['id']}", type="secondary"
        ):
            # La petición al endpoint de detalle sólo se realiza al abrir el diálogo.
            render_job_details(job["id"])


def render_job_search() -> None:
    st.header("Buscar ofertas")
    st.caption("Encuentra oportunidades por rol y ubicación.")

    with st.form("job_search"):
        search_col_1, search_col_2 = st.columns(2)
        role = search_col_1.text_input(
            "Palabra clave o rol", placeholder="Ej. Python developer"
        )
        location = search_col_2.text_input(
            "Ubicación", placeholder="Ej. Madrid o Spain"
        )
        days = st.slider("Publicadas en los últimos", 1, 30, 7, format="%d días")
        submitted = st.form_submit_button("Buscar ofertas", type="primary")

    # La primera carga ya muestra resultados recientes; el formulario evita una
    # petición nueva por cada tecla que escribe el usuario.
    if submitted or "jobs" not in st.session_state:
        params = {
            "role": role.strip() or None,
            "location": location.strip() or None,
            "days": days,
            "limit": 20,
        }
        try:
            st.session_state.jobs = api_get("jobs", params=params).json()
            st.session_state.search = {
                "role": role.strip(),
                "location": location.strip(),
                "days": days,
            }
            st.session_state.jobs_error = None
        except requests.RequestException:
            st.session_state.jobs = []
            st.session_state.jobs_error = (
                "No se han podido cargar las ofertas. Comprueba que la API esté activa."
            )

    if st.session_state.get("jobs_error"):
        st.error(st.session_state.jobs_error)
        return

    jobs = st.session_state.get("jobs", [])
    st.markdown(f"### {len(jobs)} ofertas encontradas")
    if not jobs:
        st.info(
            "No hay ofertas que coincidan con estos filtros. Prueba a ampliar la búsqueda."
        )
        return

    for job in jobs:
        render_job_card(job)


def render_company_ranking() -> None:
    st.header("Empresas con más ofertas")
    st.caption("Ranking según las ofertas almacenadas actualmente.")

    try:
        companies = api_get("stats/top-companies", params={"limit": 10}).json()
    except requests.RequestException:
        st.error("No se ha podido cargar el ranking de empresas.")
        return

    if not companies:
        st.info("Todavía no hay datos suficientes para crear el ranking.")
        return

    largest_count = companies[0]["job_count"] or 1
    total_top_jobs = sum(item["job_count"] for item in companies)

    for position, item in enumerate(companies, start=1):
        company = item.get("company") or {}
        count = item.get("job_count", 0)
        with st.container(border=True):
            rank_col, company_col, count_col = st.columns([0.6, 4, 1.4])
            rank_col.markdown(f"## {position}")
            company_col.markdown(f"**{company.get('name') or 'Empresa no indicada'}**")
            if company.get("website"):
                company_col.markdown(f"[Visitar web ↗]({company['website']})")
            else:
                company_col.caption("Web no disponible")
            count_col.metric("Ofertas", count)
            st.progress(count / largest_count)
            share = (count / total_top_jobs * 100) if total_top_jobs else 0
            st.caption(f"{share:.1f}% de las ofertas de este top {len(companies)}")


st.set_page_config(page_title="Job Intelligence", page_icon="💼", layout="wide")
st.title("💼 Job Intelligence")
st.caption("Explora oportunidades y descubre qué empresas están contratando.")

tab_jobs, tab_analytics = st.tabs(["🔍 Buscar ofertas", "📊 Ranking de empresas"])

with tab_jobs:
    render_job_search()

with tab_analytics:
    render_company_ranking()
