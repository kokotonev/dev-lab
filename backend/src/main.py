from  fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/liveness")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}