from fastapi import FastAPI

app = FastAPI(
    title="Job Intelligence API",
    description="Job market intelligence and search platform",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
