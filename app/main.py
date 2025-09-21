from fastapi import FastAPI
from .core import database
from .models import user
from .api.v1 import api

user.Base.metadata.create_all(bind=database.engine) 

app = FastAPI(title="Scalable Fast API")

app.include_router(api.api_router, prefix='/api/v1')

@app.get("/")
def root():
    return {"message": "API is running"}