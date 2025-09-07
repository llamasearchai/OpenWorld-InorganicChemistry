from fastapi import FastAPI

app = FastAPI(
    title="OpenWorld-InorganicChemistry",
    description="An open-source platform for inorganic materials discovery, synthesis, and analysis using LLMs and AI Agents.",
    version="0.1.0",
)

@app.get("/health", status_code=200)
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
