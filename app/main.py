from fastapi import FastAPI

from utils import create_table
from routes import routes as router
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI()

app.include_router(router)

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": datetime.datetime.now()}

@app.on_event("startup")
async def startup_event():
    create_table()