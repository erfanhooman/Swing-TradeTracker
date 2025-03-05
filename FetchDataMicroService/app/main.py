from fastapi import FastAPI
from .api import router  # Changed from 'app.api'

app = FastAPI(title="Coin Data Microservice")
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Coin Price Microservice is running"}