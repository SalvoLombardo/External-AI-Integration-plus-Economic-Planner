from fastapi import FastAPI
from app.routes.llm_routes import ai_router

app = FastAPI(
    title="FastAPI Bridge",
    description="App che comunica con Flask e l'LLM",
    version="1.0.0",
)

# Registriamo i router
app.include_router(ai_router)
