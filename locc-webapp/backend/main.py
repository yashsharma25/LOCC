from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # restrict in prod (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

