import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routers import authentication
from src.services.exceptions import TokenValidationError

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="FastAPI backend for my demo project",
    summary="This is a simple FastAPI backend for demonstration purposes.",
    version="0.1.0",
    contact={
        "name": "Nikola Tonev",
        "email": "nstonev@gmail.com"
    }
)


# Set up CORS middleware to allow requests from the React/Vite development server
allowed_origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.exception_handler(TokenValidationError)
async def token_validation_error_handler(request: Request, exc: TokenValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)}
    )

app.include_router(authentication.router)

@app.get("/liveness")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}