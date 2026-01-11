from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core import database
from .models import user
from .api.v1 import api

user.Base.metadata.create_all(bind=database.engine) 

app = FastAPI(title="Scalable Fast API")

# CORS middleware - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(api.api_router, prefix='/api/v1')

@app.get("/")
def root():
    return {"message": "API is running"}