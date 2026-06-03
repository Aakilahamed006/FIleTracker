from fastapi import FastAPI

from app.database.repository import FileRepository
from app.watcher.event_processor import EventProcessor

app = FastAPI()

repo = FileRepository()
processor = EventProcessor(repo=repo)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
